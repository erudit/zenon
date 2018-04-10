import datetime as dt
import dateutil.relativedelta as dr
import io
import unittest.mock

from django.conf import settings
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication

from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.test import BaseEruditTestCase
from erudit.test.factories import (
    ArticleFactory,
    AuthorFactory,
    IssueFactory,
    JournalFactory,
    JournalTypeFactory,
    CollectionFactory,
    IssueContributorFactory,
    IssueThemeFactory,
)


def reldate(inc_days):
    """ Return today + inc_days. """
    now_dt = dt.date.today()
    return now_dt + dt.timedelta(days=inc_days)


class TestJournal(BaseEruditTestCase):
    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.journal.fedora_model, JournalDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.journal.erudit_class, EruditJournal)

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        # Run & check
        self.assertEqual(self.journal.pid, 'erudit:erudit.dummy139')

    def test_can_return_its_published_issues(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, year=2010)
        issue_2 = IssueFactory.create(journal=self.journal, year=2009)

        # Create an unpublished issue
        IssueFactory.create(
            journal=self.journal, is_published=False,
            year=dt.datetime.now().year + 2,
        )
        # Run & check
        self.assertEqual(set(self.journal.published_issues), {issue_1, issue_2})

    def test_can_return_when_date_embargo_begins(self):
        # Setup
        journal = JournalFactory()
        journal.open_access = False
        journal.save()
        date_issue_1 = dt.date(2017, 3, 8)
        date_issue_2 = date_issue_1 - dr.relativedelta(months=5)
        date_issue_3 = date_issue_1 + dr.relativedelta(months=5)
        IssueFactory.create(
            journal=journal, year=date_issue_1.year,
            is_published=True, date_published=date_issue_1)
        IssueFactory.create(
            journal=journal, year=date_issue_2.year,
            is_published=True, date_published=date_issue_2)
        IssueFactory.create(
            journal=journal, year=date_issue_3.year,
            is_published=False, date_published=date_issue_3)
        # Run & check
        self.assertEqual(journal.date_embargo_begins, dt.date(2017, 2, 1))

    def test_can_return_its_first_issue(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        IssueFactory.create(
            journal=self.journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year + 2,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.first_issue, issue_1)

    def test_can_return_its_last_issue(self):
        # Setup
        journal = JournalFactory()
        IssueFactory.create(
            journal=journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=journal, year=dt.datetime.now().year + 2, is_published=False,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(journal.last_issue, issue_2)

    def test_knows_if_it_is_provided_by_fedora(self):
        # Run & check
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.assertTrue(self.journal.provided_by_fedora)
        self.journal.localidentifier = None
        self.journal.save()
        self.assertFalse(self.journal.provided_by_fedora)

    def test_can_return_its_letter_prefix(self):
        # Setup
        journal_1 = JournalFactory.create(
            name='Test', collection=self.collection, publishers=[self.publisher])
        # Run & check
        self.assertEqual(journal_1.letter_prefix, 'T')

    def test_can_return_the_published_open_access_issues(self):
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        now_dt = dt.date.today()
        date_issue_1 = dt.date(now_dt.year, now_dt.month, 1)
        date_issue_2 = now_dt - dr.relativedelta(months=ml)
        date_issue_3 = dt.date(
            now_dt.year,
            now_dt.month,
            1
        ) - dr.relativedelta(months=ml)
        date_issue_4 = now_dt - dr.relativedelta(months=(ml + 5))
        date_issue_5 = now_dt - dr.relativedelta(months=((ml + 5) * 2))
        journal = JournalFactory()
        journal.open_access = False
        journal.save()
        issue_1 = IssueFactory.create(  # noqa: F841
            journal=journal, year=date_issue_1.year,
            is_published=True, date_published=date_issue_1)
        issue_2 = IssueFactory.create(  # noqa: F841
            journal=journal, year=date_issue_2.year,
            is_published=True, date_published=date_issue_2)
        issue_3 = IssueFactory.create(  # noqa: F841
            journal=journal, year=date_issue_3.year,
            is_published=True, date_published=date_issue_3)
        issue_4 = IssueFactory.create(
            journal=journal, number=2, year=date_issue_4.year,
            is_published=True, date_published=date_issue_4)
        issue_5 = IssueFactory.create(
            journal=journal, number=1, year=date_issue_5.year,
            is_published=True, date_published=date_issue_5)
        issue_6 = IssueFactory.create(
            journal=journal, number=7, year=date_issue_1.year - 10,
            is_published=True, date_published=date_issue_1, force_free_access=True)
        issue_7 = IssueFactory.create(  # noqa: F841
            journal=journal, year=date_issue_5.year,
            is_published=False, date_published=date_issue_5)
        assert set(journal.published_open_access_issues) == {issue_6, issue_5, issue_4, }

    def test_can_return_the_published_open_access_issues_period_coverage(self):
        # Setup
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        now_dt = dt.date.today()
        journal = JournalFactory()
        journal.last_publication_year = now_dt.year
        journal.open_access = False
        journal.save()
        date_issue_1 = dt.date(now_dt.year, now_dt.month, 1)
        date_issue_2 = now_dt - dr.relativedelta(months=ml)
        date_issue_3 = dt.date(
            now_dt.year,
            now_dt.month,
            1
        ) - dr.relativedelta(months=ml)
        date_issue_4 = now_dt - dr.relativedelta(months=(ml + 5))
        date_issue_5 = now_dt - dr.relativedelta(months=((ml + 5) * 2))
        IssueFactory.create(
            journal=journal, year=date_issue_1.year,
            date_published=date_issue_1)
        IssueFactory.create(
            journal=journal, year=date_issue_2.year,
            date_published=date_issue_2)
        IssueFactory.create(
            journal=journal, year=date_issue_3.year,
            date_published=date_issue_3)
        issue_4 = IssueFactory.create(
            journal=journal, year=date_issue_4.year,
            date_published=date_issue_4)
        issue_5 = IssueFactory.create(
            journal=journal, year=date_issue_5.year,
            date_published=date_issue_5)
        # Run & check
        self.assertEqual(
            journal.published_open_access_issues_period_coverage,
            {
                'from': issue_5.date_published,
                'to': issue_4.date_published
            }
        )

    def test_knows_its_directors(self):
        now_dt = dt.datetime.now()
        journal = JournalFactory()
        first_issue = IssueFactory.create(
            journal=self.journal, date_published=now_dt - dt.timedelta(days=1)
        )

        first_issue_director = IssueContributorFactory(
            issue=first_issue, is_director=True
        )

        last_issue = IssueFactory.create(journal=journal, date_published=now_dt)
        last_issue_director = IssueContributorFactory(issue=last_issue, is_director=True)

        assert last_issue_director in journal.get_directors()
        assert first_issue_director not in journal.get_directors()

    def test_knows_its_editors(self):
        journal = JournalFactory()
        first_issue = IssueFactory.create(
            journal=journal, date_published=reldate(-1)
        )
        first_issue_editor = IssueContributorFactory(issue=first_issue, is_editor=True)

        last_issue = IssueFactory.create(journal=journal, date_published=reldate(0))
        last_issue_editor = IssueContributorFactory(issue=last_issue, is_editor=True)

        assert last_issue_editor in journal.get_editors()
        assert first_issue_editor not in journal.get_editors()

    def test_published_issues_uses_fedora_order(self):
        # The `published_issues` queryset returns a list that uses order fetched from fedora.
        journal = JournalFactory.create()
        issue1 = IssueFactory.create(journal=journal)
        issue2 = IssueFactory.create(journal=journal)
        issue3 = IssueFactory.create(journal=journal)
        ordered_issues = [issue3, issue1, issue2]
        ordered_pids = [i.get_full_identifier() for i in ordered_issues]
        journal.erudit_object = unittest.mock.MagicMock()
        journal.erudit_object.get_published_issues_pids = unittest.mock.MagicMock(
            return_value=ordered_pids)

        assert list(journal.published_issues.all()) == ordered_issues

    def test_published_issues_can_mix_fedora_and_non_fedora(self):
        # A journal with incomplete fedora PIDs are "mixed" journals who left Erudit. We keep
        # old issues in Fedora but redirect new issues wherever they are.
        # It's thus possible to have some issues that aren't part of the PID list. In these cases,
        # we put these issues *before* those in the PID list, in -date_published order.
        i1 = IssueFactory.create()
        i2 = IssueFactory.create_published_after(i1)
        # non-fedora
        i3 = IssueFactory.create_published_after(i2, localidentifier=None)
        i4 = IssueFactory.create_published_after(i3, localidentifier=None)
        ordered_fedora_issues = [i1, i2]
        ordered_pids = [i.get_full_identifier() for i in ordered_fedora_issues]
        i1.journal.erudit_object = unittest.mock.MagicMock()
        i1.journal.erudit_object.get_published_issues_pids = unittest.mock.MagicMock(
            return_value=ordered_pids)

        assert list(i1.journal.published_issues.all()) == [i4, i3, i1, i2]

    def test_published_issues_missing_pid(self):
        # When a PID is missing from the PID list *but* that the issue is a fedora one, put that
        # issue at the *end* of the list. We do that because cases of missing issues are most
        # likely old issues and we don't want them to end up being considered as the journal's
        # latest issue. See #1664
        i1 = IssueFactory.create()
        i2 = IssueFactory.create_published_after(i1)
        ordered_fedora_issues = [i2]
        ordered_pids = [i.get_full_identifier() for i in ordered_fedora_issues]
        i1.journal.erudit_object = unittest.mock.MagicMock()
        i1.journal.erudit_object.get_published_issues_pids = unittest.mock.MagicMock(
            return_value=ordered_pids)

        assert list(i1.journal.published_issues.all()) == [i2, i1]


class TestIssue(BaseEruditTestCase):
    def setUp(self):
        super(TestIssue, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)

    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.issue.fedora_model, PublicationDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.issue.erudit_class, EruditPublication)

    def test_can_return_its_full_identifier(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.get_full_identifier(), 'erudit:erudit.dummy139.dummy1234')

    def test_issue_has_no_full_identifier_if_a_part_is_missing(self):
        self.journal.localidentifier = "dummy139"
        self.journal.save()
        self.issue.localidentifier = None
        self.issue.save()

        assert self.issue.get_full_identifier() is None

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.pid, 'erudit:erudit.dummy139.dummy1234')

    def test_knows_if_it_is_embargoed_in_case_of_scientific_journals(self):
        # Setup
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        journal = JournalFactory(collection=self.collection)
        now_dt = dt.date.today()
        journal.last_publication_year = now_dt.year
        journal.open_access = False
        journal.save()
        date_issue_1 = dt.date(now_dt.year, now_dt.month, 1)
        date_issue_2 = now_dt - dr.relativedelta(months=ml)
        date_issue_3 = dt.date(
            now_dt.year,
            now_dt.month,
            1
        ) - dr.relativedelta(months=ml)
        date_issue_4 = now_dt - dr.relativedelta(months=(ml + 5))
        date_issue_5 = now_dt - dr.relativedelta(months=((ml + 5) * 2))
        issue_1 = IssueFactory.create(
            journal=journal, year=date_issue_1.year,
            date_published=date_issue_1)
        issue_2 = IssueFactory.create(
            journal=journal, year=date_issue_2.year,
            date_published=date_issue_2)
        issue_3 = IssueFactory.create(
            journal=journal, year=date_issue_3.year,
            date_published=date_issue_3)
        issue_4 = IssueFactory.create(
            journal=journal, year=date_issue_4.year,
            date_published=date_issue_4)
        issue_5 = IssueFactory.create(
            journal=journal, year=date_issue_5.year,
            date_published=date_issue_5)
        issue_6 = IssueFactory.create(
            journal=journal, year=date_issue_1.year - 10,
            date_published=date_issue_1)
        issue_7 = IssueFactory.create(
            journal=journal, year=date_issue_1.year - 10,
            date_published=date_issue_1, force_free_access=True)
        # Run & check
        self.assertTrue(issue_1.embargoed)
        self.assertTrue(issue_2.embargoed)
        self.assertTrue(issue_3.embargoed)
        self.assertFalse(issue_4.embargoed)
        self.assertFalse(issue_5.embargoed)
        self.assertTrue(issue_6.embargoed)
        self.assertFalse(issue_7.embargoed)

    def test_knows_if_it_is_embargoed_in_case_of_non_scientific_journals(self):
        # Setup
        from erudit.conf.settings import CULTURAL_JOURNAL_EMBARGO_IN_MONTHS as ml
        journal = JournalFactory(
            type_code='C', collection=self.collection)
        now_dt = dt.date.today()
        journal.last_publication_year = now_dt.year
        journal.open_access = False
        journal.save()
        date_issue_1 = dt.date(now_dt.year, now_dt.month, 1)
        date_issue_2 = now_dt - dr.relativedelta(months=ml)
        date_issue_3 = dt.date(
            now_dt.year,
            now_dt.month,
            1
        ) - dr.relativedelta(months=ml)
        date_issue_4 = now_dt - dr.relativedelta(months=(ml + 5))
        date_issue_5 = now_dt - dr.relativedelta(months=((ml + 5) * 2))
        issue_1 = IssueFactory.create(
            journal=journal, year=date_issue_1.year,
            date_published=date_issue_1)
        issue_2 = IssueFactory.create(
            journal=journal, year=date_issue_2.year,
            date_published=date_issue_2)
        issue_3 = IssueFactory.create(
            journal=journal, year=date_issue_3.year,
            date_published=date_issue_3)
        issue_4 = IssueFactory.create(
            journal=journal, year=date_issue_4.year,
            date_published=date_issue_4)
        issue_5 = IssueFactory.create(
            journal=journal, year=date_issue_5.year,
            date_published=date_issue_5)
        issue_6 = IssueFactory.create(
            journal=journal, year=date_issue_1.year - 10,
            date_published=date_issue_1)
        issue_7 = IssueFactory.create(
            journal=journal, year=date_issue_5.year - 10,
            date_published=date_issue_5, force_free_access=True)
        # Run & check
        self.assertTrue(issue_1.embargoed)
        self.assertTrue(issue_2.embargoed)
        self.assertTrue(issue_3.embargoed)
        self.assertFalse(issue_4.embargoed)
        self.assertFalse(issue_5.embargoed)
        self.assertTrue(issue_6.embargoed)
        self.assertFalse(issue_7.embargoed)

    def test_issues_with_a_next_year_published_date_are_embargoed(self):
        now_dt = dt.datetime.now()
        journal = JournalFactory(
            type_code='C', collection=self.collection)
        journal.last_publication_year = now_dt.year + 1
        journal.save()
        issue = IssueFactory.create(
            journal=journal,
            year=now_dt.year + 1, date_published=dt.date(now_dt.year + 1, 1, 1)
        )
        assert issue.embargoed is True

    def test_knows_that_issues_with_open_access_are_not_embargoed(self):
        # Setup
        now_dt = dt.datetime.now()
        journal = JournalFactory()
        j2 = JournalFactory.create(
            type_code='C',
            open_access=False,
            collection=CollectionFactory.create(code='not-erudit'),
        )
        journal.last_publication_year = now_dt.year
        journal.open_access = True
        journal.save()
        issue_1 = IssueFactory.create(
            journal=journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_2 = IssueFactory.create(
            journal=journal, year=now_dt.year - 2,
            date_published=dt.date(now_dt.year - 2, 3, 20))
        issue_3 = IssueFactory.create(
            journal=j2, year=now_dt.year,
            date_published=dt.date(now_dt.year, 3, 20))
        # Run & check
        self.assertFalse(issue_1.embargoed)
        self.assertFalse(issue_2.embargoed)
        self.assertFalse(issue_3.embargoed)

    def test_knows_if_it_has_a_coverpage(self):
        # Setup
        journal = JournalFactory()
        journal.open_access = True
        journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage.png', 'rb') as f:
            issue_1 = IssueFactory.create(journal=journal)
            issue_2 = IssueFactory.create(journal=journal)
            issue_1.fedora_object = unittest.mock.MagicMock()
            issue_1.fedora_object.pid = "pid"
            issue_1.fedora_object.coverpage = unittest.mock.MagicMock()
            issue_1.fedora_object.coverpage.content = io.BytesIO(f.read())
            issue_2.fedora_object = unittest.mock.MagicMock()
            issue_2.fedora_object.pid = "pid2"
            issue_2.fedora_object.coverpage = unittest.mock.MagicMock()
            issue_2.fedora_object.coverpage.content = ''
        # We don't crash trying to check the fedora object. We return False
        issue_3 = IssueFactory.create(journal=journal)

        # Run & check
        self.assertTrue(issue_1.has_coverpage)
        self.assertFalse(issue_2.has_coverpage)
        self.assertFalse(issue_3.has_coverpage)

    def test_knows_that_an_issue_with_an_empty_coverpage_has_no_coverpage(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage_empty.png', 'rb') as f:
            issue = IssueFactory.create(journal=self.journal)
            issue.fedora_object = unittest.mock.MagicMock()
            issue.fedora_object.pid = "issue"
            issue.fedora_object.coverpage = unittest.mock.MagicMock()
            issue.fedora_object.coverpage.content = io.BytesIO(f.read())

        # Run & check
        self.assertFalse(issue.has_coverpage)

    def test_can_return_a_slug_that_can_be_used_in_urls(self):
        # Setup
        issue_1 = IssueFactory.create(
            year=2015, volume='4', number='1', localidentifier='i1')
        issue_2 = IssueFactory.create(
            year=2015, volume='4', number=None, localidentifier='i2')
        issue_3 = IssueFactory.create(
            year=2015, volume=None, number='2', localidentifier='i3')
        issue_4 = IssueFactory.create(
            year=2015, volume='2-3', number='39', localidentifier='i4')
        issue_5 = IssueFactory.create(
            year=2015, volume=None, number=None, localidentifier='i5')
        issue_6 = IssueFactory.create(
            year=2015, volume='2 bis', number='39', localidentifier='i6')
        # Run & check
        self.assertEqual(issue_1.volume_slug, '2015-v4-n1')
        self.assertEqual(issue_2.volume_slug, '2015-v4')
        self.assertEqual(issue_3.volume_slug, '2015-n2')
        self.assertEqual(issue_4.volume_slug, '2015-v2-3-n39')
        self.assertEqual(issue_5.volume_slug, '2015')
        self.assertEqual(issue_6.volume_slug, '2015-v2-bis-n39')

    def test_knows_its_directors(self):
        contributor = IssueContributorFactory(issue=self.issue, is_director=True)
        assert contributor in self.issue.get_directors()

    def test_knows_its_editors(self):
        contributor = IssueContributorFactory(issue=self.issue, is_editor=True)
        assert contributor in self.issue.get_editors()

    def test_can_return_its_name_with_themes(self):
        theme1 = IssueThemeFactory(issue=self.issue)
        assert self.issue.name_with_themes == "{html_name}: {html_subname}".format(
            html_name=theme1.html_name, html_subname=theme1.html_subname
        )

        theme2 = IssueThemeFactory(issue=self.issue)
        assert self.issue.name_with_themes == "{html_name}: {html_subname} / {html_name2}: {html_subname2}".format(  # noqa
            html_name=theme1.html_name, html_subname=theme1.html_subname,
            html_name2=theme2.html_name, html_subname2=theme2.html_subname,
        )


class TestIssueContributor(BaseEruditTestCase):

    def test_can_format_its_name(self):
        contributor = IssueContributorFactory(
            firstname="Tryphon",
            lastname=None,
            role_name=None
        )

        assert contributor.format_name() == "Tryphon"

        contributor = IssueContributorFactory(
            firstname="Tryphon",
            lastname="Tournesol",
            role_name=None
        )

        assert contributor.format_name() == "Tryphon Tournesol"

        contributor = IssueContributorFactory(
            firstname="Tryphon",
            lastname="Tournesol",
            role_name="Professeur"
        )

        assert contributor.format_name() == "Tryphon Tournesol (Professeur)"


class TestArticle(BaseEruditTestCase):

    def setUp(self):
        super(TestArticle, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)
        self.article = ArticleFactory.create(issue=self.issue)

    def test_only_has_fedora_object_if_collection_has_localidentifier(self):
        c1 = CollectionFactory.create(localidentifier=None)
        j1 = JournalFactory.create(collection=c1)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        assert article_1.fedora_object is None

    def test_only_has_full_identifier_if_complete(self):
        c1 = CollectionFactory.create(localidentifier=None)

        j1 = JournalFactory.create(collection=c1, localidentifier=None)
        i1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=i1)

        assert article_1.get_full_identifier() is None

        i1.localidentifier = 'issue1'
        i1.save()
        assert article_1.get_full_identifier() is None

        j1.localidentifier = 'journal1'
        j1.save()
        assert article_1.get_full_identifier() is None

        c1.localidentifier = 'c1'
        c1.save()
        assert article_1.get_full_identifier() is not None

    def test_knows_that_it_is_in_open_access_if_its_issue_is_in_open_access(self):
        # Setup
        j1 = JournalFactory.create(open_access=True)
        j2 = JournalFactory.create(open_access=False)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_is_in_open_access_if_its_journal_is_in_open_access(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        j2 = JournalFactory.create(open_access=False)
        issue_1 = IssueFactory.create(journal=self.journal)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_is_embargoed(self):
        # Setup
        now_dt = dt.date.today()
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        journal = JournalFactory(collection=self.collection)
        journal.open_access = False
        journal.last_publication_year = now_dt.year
        journal.save()
        date_issue_1 = dt.date(now_dt.year, now_dt.month, 1)
        date_issue_2 = now_dt - dr.relativedelta(months=ml)
        date_issue_3 = dt.date(
            now_dt.year,
            now_dt.month,
            1
        ) - dr.relativedelta(months=ml)
        date_issue_4 = now_dt - dr.relativedelta(months=(ml + 5))
        date_issue_5 = now_dt - dr.relativedelta(months=((ml + 5) * 2))
        issue_1 = IssueFactory.create(
            journal=journal, year=date_issue_1.year,
            date_published=date_issue_1)
        issue_2 = IssueFactory.create(
            journal=journal, year=date_issue_2.year,
            date_published=date_issue_2)
        issue_3 = IssueFactory.create(
            journal=journal, year=date_issue_3.year,
            date_published=date_issue_3)
        issue_4 = IssueFactory.create(
            journal=journal, year=date_issue_4.year,
            date_published=date_issue_4)
        issue_5 = IssueFactory.create(
            journal=journal, year=date_issue_5.year,
            date_published=date_issue_5)
        article_1 = ArticleFactory.create(issue=issue_1)
        article_2 = ArticleFactory.create(issue=issue_2)
        article_3 = ArticleFactory.create(issue=issue_3)
        article_4 = ArticleFactory.create(issue=issue_4)
        article_5 = ArticleFactory.create(issue=issue_5)
        # Run & check
        self.assertTrue(article_1.embargoed)
        self.assertTrue(article_2.embargoed)
        self.assertTrue(article_3.embargoed)
        self.assertFalse(article_4.embargoed)
        self.assertFalse(article_5.embargoed)


class TestAuthor(BaseEruditTestCase):
    def test_can_return_articles_written_for_a_given_journal(self):
        # Setup
        other_journal = JournalFactory.create(
            publishers=[self.publisher])
        other_issue = IssueFactory.create(
            journal=other_journal, date_published=dt.datetime.now())
        other_article = ArticleFactory.create(issue=other_issue)

        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)

        author = AuthorFactory.create()

        article.authors.add(author)
        other_article.authors.add(author)

        # Run
        self.assertEqual(list(author.articles_in_journal(self.journal)), [article, ])

    def test_can_return_its_letter_prefix(self):
        # Setup
        author_1 = AuthorFactory.create(lastname='Abc', firstname='Def')
        author_2 = AuthorFactory.create(lastname=None, firstname='Def')
        author_3 = AuthorFactory.create(lastname=None, firstname='Def', othername='Ghi')
        author_4 = AuthorFactory.create(lastname=':', firstname='Def')
        author_5 = AuthorFactory.create(lastname=':', firstname=None)

        # Run & check
        assert author_1.letter_prefix == 'A'
        assert author_2.letter_prefix == 'D'
        assert author_3.letter_prefix == 'G'
        assert author_4.letter_prefix == 'D'
        assert author_5.letter_prefix is None

    def test_can_return_abbreviated_volume_title_when_not_in_fedora(self):
        issue1 = IssueFactory(volume=1, number=2, publication_period='may', localidentifier=None)
        issue2 = IssueFactory(volume=1, number=None, publication_period='may', localidentifier=None)
        issue3 = IssueFactory(number=2, publication_period='may', localidentifier=None)

        assert issue1.abbreviated_volume_title == 'Vol. 1, n<sup>o</sup> 2, may'
        assert issue2.abbreviated_volume_title == 'Vol. 1, may'
        assert issue3.abbreviated_volume_title == 'N<sup>o</sup> 2, may'

    def test_can_return_its_name(self):
        author_1 = AuthorFactory()

        assert str(author_1) == "{firstname} {lastname}".format(
            lastname=author_1.lastname, firstname=author_1.firstname
        )

        author_1.suffix = 'PhD'

        assert str(author_1) == "{suffix} {firstname} {lastname}".format(
            suffix=author_1.suffix, firstname=author_1.firstname, lastname=author_1.lastname
        )

    def test_journaltype_can_return_embargo_duration_in_days(self):
        journal_type = JournalTypeFactory.create(code='S')
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        duration = dt.date.today() - (dt.date.today() - dr.relativedelta(months=ml))
        assert journal_type.embargo_duration(unit="days") == duration.days
