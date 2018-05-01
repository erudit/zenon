import datetime as dt
import structlog
import re
import urllib.parse

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.encoding import smart_str
from eruditarticle.objects import EruditArticle
from eruditarticle.utils import remove_xml_namespaces
import lxml.etree as et

from ...conf import settings as erudit_settings
from ...fedora.objects import ArticleDigitalObject
from ...fedora.objects import JournalDigitalObject
from ...fedora.objects import PublicationDigitalObject
from ...fedora.utils import get_pids
from ...fedora.utils import get_unimported_issues_pids
from ...fedora.repository import api
from ...models import Article
from ...models import Collection
from ...models import Issue
from ...models import Journal

logger = structlog.getLogger(__name__)


class Command(BaseCommand):
    """ Imports journal objects from a Fedora Commons repository.

    The command is able to import a journal object - including its issues and its articles - from
    a Fedora Commons repository. To do so, the command assumes that some journal collections
    (:py:class`Collection <erudit.models.core.Collection>` instances) are already created in the
    database.

    By default the command will try to import the journal objects that have been modified since the
    latest journal modification date stored in the database. If no journals can be found in the
    database, the command will perform a full import.
    """

    help = 'Import journals from Fedora'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true', dest='full', default=False,
            help='Perform a full import.')

        parser.add_argument(
            '--test-xslt', action='store', dest='test_xslt',
            help='Python path to a function to test the XSLT transformation of articles')

        parser.add_argument(
            '--pid', action='store', dest='journal_pid', help='Journal PID to manually import.')

        parser.add_argument(
            '--issue-pid', action='store', dest='issue_pid', help='Issue PID to manually import.')  # noqa

        parser.add_argument(
            '--import-missing', action='store_true', dest='import_missing', help='Import missing issues.'  # noqa
        )
        parser.add_argument(
            '--mdate', action='store', dest='mdate',
            help='Modification date to use to retrieve journals to import (iso format).')

    def handle(self, *args, **options):
        self.full_import = options.get('full', False)
        self.test_xslt = options.get('test_xslt', None)
        self.journal_pid = options.get('journal_pid', None)
        self.modification_date = options.get('mdate', None)
        self.journal_precendence_relations = []
        self.issue_pid = options.get('issue_pid', None)
        self.import_missing = options.get('import_missing', None)
        logger.info("import.started", **options)

        # Handles a potential XSLT test function
        try:
            assert self.test_xslt is not None
            module, xslt_test_func = self.test_xslt.rsplit('.', 1)
            module, xslt_test_func = smart_str(module), smart_str(xslt_test_func)
            xslt_test_func = getattr(__import__(module, {}, {}, [xslt_test_func]), xslt_test_func)
            self.xslt_test_func = xslt_test_func
        except ImportError:
            logger.error(
                "invalid_argument",
                xslt_test_func=self.test_xslt,
                msg="Cannot import XSLT test function"
            )
            return
        except AssertionError:
            pass

        # Handles a potential modification date option
        try:
            assert self.modification_date is not None
            self.modification_date = dt.datetime.strptime(self.modification_date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(
                "invalid_argument",
                modification_date=self.modification_date
            )
            return
        except AssertionError:
            pass

        if self.issue_pid or self.import_missing:
            if self.issue_pid:
                logger.info(
                    "import.started",
                    issue_pid=self.issue_pid,
                )
                unimported_issues_pids = [self.issue_pid]
                if not re.match(r'^\w+\:\w+\.\w+\.\w+$', self.issue_pid):
                    logger.error(
                        "invalid_argument",
                        issue_pid=self.issue_pid,
                        msg="Not a valid issue pid"
                    )
            else:
                unimported_issues_pids = get_unimported_issues_pids()
                logger.info(
                    "import.started",
                    issues_count=len(unimported_issues_pids),
                    msg="importing missing issues"
                )
            for issue_pid in unimported_issues_pids:
                journal_localidentifier = issue_pid.split(':')[1].split('.')[1]
                try:
                    journal = Journal.objects.get(localidentifier=journal_localidentifier)
                except Journal.DoesNotExist:
                    logger.error(
                        "journal.import.error",
                        journal_pid=journal_localidentifier
                    )
                    return
                try:
                    self._import_issue(issue_pid, journal)
                except Exception as e:
                    logger.error(
                        'issue.import.error',
                        issue_pid=issue_pid,
                        error=e,
                    )
            return

            # Imports a journal PID manually
        if self.journal_pid:
            logger.info(
                'journal.import.start',
                journal_pid=self.journal_pid
            )

            if not re.match(r'^\w+\:\w+\.\w+$', self.journal_pid):
                logger.error(
                    "invalid_argument",
                    journal_pid=self.journal_pid
                )
                return

            collection_localidentifier = self.journal_pid.split(':')[1].split('.')[0]
            try:
                collection = Collection.objects.get(localidentifier=collection_localidentifier)
            except Collection.DoesNotExist:
                logger.error(
                    "invalid_argument",
                    msg="Collection does not exist",
                    collection_pid=collection_localidentifier
                )
                return

            self.import_journal(self.journal_pid, collection)
            self.import_journal_precedences(self.journal_precendence_relations)
            return

        # Imports each collection
        journal_count, journal_errored_count = 0, 0
        issue_count, issue_errored_count, article_count = 0, 0, 0
        for collection_config in erudit_settings.JOURNAL_PROVIDERS.get('fedora'):
            collection_code = collection_config.get('collection_code')
            try:
                collection = Collection.objects.get(code=collection_code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(
                    code=collection_code, name=collection_config.get('collection_title'),
                    localidentifier=collection_config.get('localidentifier'))
            else:
                _jc, _jec, _ic, _iec, _ac = self.import_collection(collection)
                journal_count += _jc
                journal_errored_count += _jec
                issue_count += _ic
                issue_errored_count += _iec
                article_count += _ac

        logger.info(
            "import.finished",
            journal_count=journal_count,
            journal_errored=journal_errored_count,
            issue_count=issue_count,
            issue_errored_count=issue_errored_count,
            article_count=article_count
        )

    def import_collection(self, collection):
        """ Imports all the journals of a specific collection. """

        self.journal_precendence_relations = []

        latest_update_date = self.modification_date
        if not self.full_import and latest_update_date is None:
            # Tries to fetch the date of the Journal instance with the more recent update date.
            latest_journal_update = Journal.objects.order_by('-fedora_updated').first()
            latest_update_date = latest_journal_update.fedora_updated.date() \
                if latest_journal_update else None

        latest_issue_update_date = self.modification_date
        if not self.full_import and latest_issue_update_date is None:
            # Tries to fetch the date of the Issue instance with the more recent update date.
            latest_issue_update = Issue.objects.order_by('-fedora_updated').first()
            latest_issue_update_date = latest_issue_update.fedora_updated.date() \
                if latest_issue_update else None

        # STEP 1: fetches the PIDs of the journals that will be imported
        # --

        base_fedora_query = "pid~erudit:{collectionid}.* label='Series Erudit'".format(
            collectionid=collection.localidentifier)
        if self.full_import or latest_update_date is None:
            modification_date = None
            full_import = True
            journal_pids = get_pids(base_fedora_query)
        else:
            modification_date = latest_update_date.isoformat()
            full_import = False
            # Fetches the PIDs of all the journals that have been update since the latest
            # modification date.
            journal_pids = get_pids(
                base_fedora_query + ' mdate>{}'.format(latest_update_date.isoformat()))
        logger.info(
            "import.started",
            collection_code=collection.code,
            full_import=full_import,
            modification_date=modification_date
        )

        # STEP 2: import each journal using its PID
        # --

        journal_count, journal_errored_count = 0, 0
        for jpid in journal_pids:
            try:
                self.import_journal(jpid, collection, False)
            except Exception as e:
                journal_errored_count += 1
                logger.error(
                    "journal.import.error",
                    journal_pid=jpid
                )
            else:
                journal_count += 1

        # STEP 3: associates Journal instances with other each other
        # --

        self.import_journal_precedences(self.journal_precendence_relations)

        # STEP 4: fetches the PIDs of the issues that will be imported
        # --
        issue_fedora_query = "pid~erudit:{collectionid}.*.* label='Publication Erudit'".format(
            collectionid=collection.localidentifier)
        if self.full_import or latest_update_date is None:
            issue_pids = get_pids(issue_fedora_query)
        else:
            # Fetches the PIDs of all the issues that have been update since the latest
            # modification date.
            issue_pids = get_pids(
                issue_fedora_query + ' mdate>{}'.format(latest_issue_update_date.isoformat()))

        # STEP 5: import each issue using its PID
        # --

        issue_count, issue_errored_count, article_count = 0, 0, 0

        for ipid in issue_pids:
            try:
                journal_localidentifier = ipid.split(':')[1].split('.')[1]
                journal = Journal.objects.get(localidentifier=journal_localidentifier)
            except Journal.DoesNotExist:
                issue_errored_count += 1
                logger.error(
                    "issue.import.error",
                    msg="Journal does not exist",
                    issue_pid=ipid,
                    journal_pid=journal_localidentifier
                )
            else:
                try:
                    _ac = self._import_issue(ipid, journal)
                except Exception as e:
                    issue_errored_count += 1
                    logger.error(
                        "issue.import.error",
                        issue_pid=ipid
                    )
                else:
                    issue_count += 1
                    article_count += _ac

        return journal_count, journal_errored_count, issue_count, issue_errored_count, article_count

    def import_journal_precedences(self, precendences_relations):
        """ Associates previous/next Journal instances with each journal. """
        for r in precendences_relations:
            localid = r['journal_localid']
            previous_localid = r['previous_localid']
            next_localid = r['next_localid']
            if previous_localid is None and next_localid is None:
                continue
            try:
                j = Journal.objects.get(localidentifier=localid)
                previous_journal = Journal.objects.get(localidentifier=previous_localid) \
                    if previous_localid else None
                next_journal = Journal.objects.get(localidentifier=next_localid) \
                    if next_localid else None
            except Journal.DoesNotExist:
                logger.error(
                    "journal.import.error",
                    journal_pid=localid,
                    msg="Unable to import precedences for journal"
                )
            else:
                j.previous_journal = previous_journal
                j.next_journal = next_journal
                j.save()

    @transaction.atomic
    def import_journal(self, journal_pid, collection, import_issues=True):
        """ Imports a journal using its PID. """
        logger.info("journal.import.start", journal=journal_pid)
        # STEP 1: fetches the full Journal fedora object
        # --

        try:
            fedora_journal = JournalDigitalObject(api, journal_pid)
            assert fedora_journal.exists
        except AssertionError:
            msg = 'The journal with PID "{}" seems to be inexistant'.format(journal_pid)
            logger.error("journal.import.error", msg=msg)
            return  # We return here in order to try to import the other journals of the collection

        # STEP 2: creates or updates the journal object
        # --

        oaiset_info_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.oaiset_info.content.serialize())) \
            if fedora_journal.oaiset_info.exists else None
        rels_ext_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.rels_ext.content.serialize())) \
            if fedora_journal.rels_ext.exists else None
        publications_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.publications.content.serialize()))
        # Set the proper values on the Journal instance
        xml_name = oaiset_info_tree.find('.//title') if oaiset_info_tree \
            else rels_ext_tree.find('.//setName')

        # Fetches the Journal instance... or creates a new one
        journal_localidentifier = journal_pid.split('.')[-1]
        try:
            journal = Journal.objects.get(localidentifier=journal_localidentifier)
        except Journal.DoesNotExist:
            journal = Journal()
            journal.localidentifier = journal_localidentifier
            journal.collection = collection
            journal.fedora_created = fedora_journal.created
            journal.name = xml_name.text if xml_name is not None else None

        xml_issue = publications_tree.xpath(
            './/numero[starts-with(@pid, "{0}")]'.format(journal_pid))
        journal.first_publication_year = journal.erudit_object.first_publication_year
        journal.last_publication_year = journal.erudit_object.last_publication_year

        # Some journals share the same code in the Fedora repository so we have to ensure that our
        # journal instances' codes are not duplicated!
        if not journal.id:
            code_base = xml_issue[0].get('revAbr') if xml_issue is not None else None
            code_base = code_base if code_base else re.sub(r'\d', '', journal_localidentifier)
            code_ext = 1
            journal.code = code_base
            while Journal.objects.filter(code=journal.code).exists():
                journal.code = code_base + str(code_ext)
                code_ext += 1

        issues = xml_issue = publications_tree.xpath('.//numero')
        current_journal_localid_found = False
        precendences_relation = {
            'journal_localid': journal.localidentifier,
            'previous_localid': None,
            'next_localid': None,
        }
        for issue in issues:
            issue_pid = issue.get('pid')
            journal_localid = issue_pid.split('.')[-2]
            if journal_localid != journal.localidentifier and not current_journal_localid_found:
                precendences_relation['next_localid'] = journal_localid
            elif journal_localid != journal.localidentifier and current_journal_localid_found:
                precendences_relation['previous_localid'] = journal_localid
            elif journal_localid == journal.localidentifier:
                current_journal_localid_found = True
        self.journal_precendence_relations.append(precendences_relation)

        journal_created = journal.id is None

        journal.fedora_updated = fedora_journal.modified
        journal.save()

        if journal_created:
            logger.info(
                "journal.created",
                journal_name=journal.name
            )
        else:
            logger.debug(
                "journal.updated",
                journal_name=journal.name
            )

        # STEP 3: imports all the issues associated with the journal
        # --
        if import_issues is False:
            return 0, 0

        issue_count, article_count = 0, 0

        issue_fedora_query = "pid~erudit:{collectionid}.{journalid}.* label='Publication Erudit'"
        issue_fedora_query = issue_fedora_query.format(
            collectionid=journal.collection.localidentifier,
            journalid=journal.localidentifier
        )
        issue_pids = get_pids(issue_fedora_query)
        for ipid in issue_pids:
            if ipid.startswith(journal_pid):
                # Imports the issue only if its PID is prefixed with the PID of the journal object.
                # In any other case this means that the issue is associated with another journal and
                # it will be imported later.
                _ac = self._import_issue(ipid, journal)
                issue_count += 1
                article_count += _ac

        return issue_count, article_count

    @transaction.atomic
    def _import_issue(self, issue_pid, journal):
        """ Imports an issue using its PID. """
        logger.info(
            "issue.import.start",
            issue_pid=issue_pid
        )

        # STEP 1: fetches the full Issue fedora object
        # --

        try:
            fedora_issue = PublicationDigitalObject(api, issue_pid)
            assert fedora_issue.exists
        except AssertionError:
            logger.error(
                'issue.import.error',
                issue_pid=issue_pid,
                msg='Issue pid nonexistent'
            )
            raise

        # STEP 2: creates or updates the issue object
        # --

        # Fetches the Issue instance... or creates a new one
        issue_localidentifier = issue_pid.split('.')[-1]
        try:
            issue = Issue.objects.get(localidentifier=issue_localidentifier)
        except Issue.DoesNotExist:
            issue = Issue()
            issue.localidentifier = issue_localidentifier
            issue.journal = journal
            issue.fedora_created = fedora_issue.created

        summary_tree = remove_xml_namespaces(
            et.fromstring(fedora_issue.summary.content.serialize()))

        # Set the proper values on the Issue instance
        issue.year = issue.erudit_object.publication_year
        issue.publication_period = issue.erudit_object.publication_period
        issue.volume = issue.erudit_object.volume
        issue.number = issue.erudit_object.number
        issue.first_page = issue.erudit_object.first_page
        issue.last_page = issue.erudit_object.last_page
        issue.title = issue.erudit_object.theme
        issue.html_title = issue.erudit_object.html_theme
        issue.thematic_issue = issue.erudit_object.theme is not None
        issue.date_published = issue.erudit_object.publication_date \
            or dt.datetime(int(issue.year), 1, 1)
        issue.date_produced = issue.erudit_object.production_date \
            or issue.erudit_object.publication_date
        issue.fedora_updated = fedora_issue.modified
        # TODO: uncomment this when we're confident about milestone 70
        # issue.is_published = issue_pid in journal.erudit_object.get_published_issues_pids()
        issue.save()

        # STEP 4: patches the journal associated with the issue
        # --

        # Journal name
        if journal.name is None:
            journal.name = issue.erudit_object.get_journal_title(formatted=True)
        journal.save()

        # STEP 5: imports all the articles associated with the issue
        # --

        article_count = 0
        localidentifiers = []

        xml_article_nodes = summary_tree.findall('.//article')
        for article_node in xml_article_nodes:
            try:
                localidentifier = article_node.get('idproprio')
                localidentifiers.append(localidentifier)
                apid = '.'.join([issue_pid, localidentifier])
                self._import_article(apid, article_node, issue)
            except Exception as e:
                logger.error(
                    'article.import.error',
                    article_pid=apid,
                )
                raise
            else:
                article_count += 1

        logger.info(
            "issue.imported",
            issue_pid=issue.pid
        )

        # STEP 6: Clean local articles that aren't referenced in our fedora issue
        # --
        # WARNING: This is done **only** with unpublished issues. We never want to delete published
        # articles from the DB, we would lose all FKs pointing to it such as bookmarks. We want to
        # delete unreferenced articles from unpublished issues because sometimes, before
        # publication, we mess up and create bad articles. We don't want them to stick in the DB
        # forever.

        if not issue.is_published:
            unreferenced_articles = issue.articles.exclude(localidentifier__in=localidentifiers)
            for article in unreferenced_articles.all():
                article.delete()
                logger.warn(
                    'article.delete',
                    article_pid=article.get_full_identifier(),
                )

        return article_count

    def _import_article(self, article_pid, issue_article_node, issue):
        """ Imports an article using its PID. """

        # STEP 1: fetches the full Article fedora object
        # --

        try:
            fedora_article = ArticleDigitalObject(api, article_pid)
            assert fedora_article.exists
        except AssertionError:
            # FIXME handle this more elegantly
            #
            # A hack has been used to implement continuous publication for ageo.
            # The consequence of this hack is that issue summaries reference articles that do not
            # exist in Fedora. To bypass this, we silently ignore non-existent articles for ageo.
            #
            # ref https://redmine.erudit.team/issues/2296
            if "ageo1499289" in article_pid:
                logger.warn(
                    'article.import.skip',
                    article_pid='ageo1499289'
                )
                return
            else:
                logger.error(
                    'article.import.error',
                    article_pid=article_pid,
                    msg='Article does not exist'
                )
                raise

        # STEP 2: creates or updates the article object
        # --

        # Fetches the Article instance... or creates a new one
        article_localidentifier = article_pid.split('.')[-1]
        try:
            article = Article.objects.get(localidentifier=article_localidentifier)
        except Article.DoesNotExist:
            article = Article()
            article.localidentifier = article_localidentifier
            article.issue = issue
            article.fedora_created = fedora_article.created

        article.fedora_updated = fedora_article.modified

        urlnode = issue_article_node.find('.//urlhtml')
        urlnode = issue_article_node.find('.//urlpdf') if urlnode is None else urlnode
        is_external_article = False
        if urlnode is not None:
            urlnode_parsed = urllib.parse.urlparse(urlnode.text)
            is_external_article = len(urlnode_parsed.netloc) and \
                'erudit.org' not in urlnode_parsed.netloc

        if is_external_article:
            self._import_article_from_issue_node(article, issue_article_node)
        elif fedora_article.erudit_xsd300.exists:
            self._import_article_from_eruditarticle_v3(article, issue_article_node)

    def _import_article_from_issue_node(self, article, issue_article_node):
        """ Imports an article using its definition in the issue's summary. """
        xml = et.tostring(issue_article_node)
        erudit_object = EruditArticle(xml)
        self._import_article_from_eruditarticle_v3(
            article,
            issue_article_node,
            article_erudit_object=erudit_object
        )

        urlhtml = issue_article_node.find('.//urlhtml')
        urlpdf = issue_article_node.find('.//urlpdf')
        article.external_url = urlhtml.text if urlhtml is not None else urlpdf.text
        if urlpdf is not None:
            article.external_pdf_url = urlpdf.text
        article.save()

    def _get_is_publication_allowed(self, issue_article_node):
        """ Return True if the publication of this article is allowed """
        accessible = issue_article_node.find('accessible')
        if accessible is not None and accessible.text == 'non':
            return False
        return True

    def _import_article_from_eruditarticle_v3(
        self, article, issue_article_node, article_erudit_object=None
    ):
        """ Imports an article using the EruditArticle v3 specification. """
        article.publication_allowed = self._get_is_publication_allowed(issue_article_node)
        article.sync_with_erudit_object(article_erudit_object)
        self.clean()
        self.save()

        if self.test_xslt:
            try:
                self.xslt_test_func({}, article)
            except Exception as e:
                logger.error(
                    'article.xslt.error',
                    article_pid=article.pid,
                    msg='Cannot perform XSLT transformation'
                )
