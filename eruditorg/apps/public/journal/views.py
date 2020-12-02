from collections import OrderedDict
from itertools import groupby
from operator import attrgetter
from string import ascii_uppercase
import io
from typing import List

import functools
import pysolr
import random
import structlog
import unicodedata

from django.conf import settings
from django.templatetags.static import static
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import Http404
from django.http.response import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.db.models import Prefetch, Q

from rules.contrib.views import PermissionRequiredMixin
from lxml import etree as et

from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import MediaDigitalObject
from erudit.fedora.objects import PageDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.fedora.views.generic import FedoraFileDatastreamView
from erudit.models import Discipline
from erudit.models import Article
from erudit.models import Journal
from erudit.models import Issue

from erudit.utils import locale_aware_sort, qs_cache_key

from base.pdf import add_coverpage_to_pdf, get_pdf_first_page
from core.metrics.metric import metric
from core.subscription.models import JournalAccessSubscription, InstitutionIPAddressRange
from apps.public.viewmixins import FallbackAbsoluteUrlViewMixin, FallbackObjectViewMixin
from apps.public.campaign.models import Campaign

from .article_access_log import ArticleAccessType
from .forms import JournalListFilterForm
from .templateannotations import IssueAnnotator
from .viewmixins import (
    ArticleAccessLogMixin,
    ArticleViewMetricCaptureMixin,
    ContentAccessCheckMixin,
    ContributorsMixin,
    PrepublicationTokenRequiredMixin,
    SingleArticleMixin,
    SingleArticleWithScholarMetadataMixin,
    SingleJournalMixin,
    SolrDataMixin,
)

from . import solr

from .coverpage import get_coverpage

logger = structlog.get_logger(__name__)


class JournalListView(FallbackAbsoluteUrlViewMixin, ListView):
    """
    Displays a list of Journal instances.
    """
    context_object_name = 'journals'
    filter_form_class = JournalListFilterForm
    model = Journal

    fallback_url = '/revue'

    def apply_sorting(self, objects):
        if self.sorting == 'name':
            objects = objects.select_related('previous_journal').select_related('next_journal')
        elif self.sorting == 'disciplines':
            objects = objects.prefetch_related('disciplines')

        objects = locale_aware_sort(objects, keyfunc=attrgetter('name'))
        if self.sorting == 'name':
            grouped = groupby(objects, key=attrgetter('letter_prefix'))
            first_pass_results = [
                {'key': g[0], 'name': g[0], 'objects': list(g[1])}
                for g in grouped]
            return first_pass_results
        elif self.sorting == 'disciplines':
            _disciplines_dict = {}
            for o in objects:
                for d in o.disciplines.all():
                    if d not in _disciplines_dict:
                        _disciplines_dict[d] = []
                    _disciplines_dict[d].append(o)

            first_pass_results = [
                {
                    'key': d.code,
                    'name': d.name,
                    'objects': _disciplines_dict[d]
                }
                for d in locale_aware_sort(_disciplines_dict, keyfunc=attrgetter('name'))
            ]

            # Only for "disciplines" sorting
            second_pass_results = []
            for r in first_pass_results:
                grouped = groupby(
                    sorted(r['objects'], key=attrgetter('collection_id')),
                    key=attrgetter('collection'))
                del r['objects']
                r['collections'] = [
                    {'key': g[0], 'objects': list(g[1])} for g in grouped]
                second_pass_results.append(r)

            return second_pass_results

    def get(self, request, *args, **kwargs):
        sorting = self.request.GET.get('sorting', 'name')
        self.sorting = sorting if sorting in ['name', 'disciplines', ] else 'name'
        self.filter_form = self.get_filter_form()
        self.filter_form.is_valid()
        self.object_list = self.get_queryset()
        context = self.get_context_data(filter_form=self.filter_form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JournalListView, self).get_context_data(**kwargs)
        context['sorting'] = self.sorting
        context['sorted_objects'] = self.apply_sorting(context.get(self.context_object_name))
        context['disciplines'] = Discipline.objects.all().order_by('name')
        context['journal_count'] = self.get_queryset().count()
        return context

    def get_filter_form(self):
        """ Returns an instance of the filter form to be used in this view. """
        return self.filter_form_class(**self.get_filter_form_kwargs())

    def get_filter_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the search form. """
        form_kwargs = {}

        if self.request.method == 'GET':
            form_kwargs.update({'data': self.request.GET, })
        return form_kwargs

    def get_queryset(self):
        qs = Journal.objects.exclude(
            pk__in=Journal.upcoming_objects.exclude(is_new=True).values_list('pk', flat=True)
        )

        # Filter the queryset
        if self.filter_form.is_valid():
            cleaned = self.filter_form.cleaned_data
            if cleaned['open_access'] and cleaned['special_open_access_opt_in']:
                qs = qs.filter(Q(open_access=True) | Q(special_open_access_opt_in=True))
            elif cleaned['special_open_access_opt_in']:
                qs = qs.filter(special_open_access_opt_in=True)
            elif cleaned['open_access']:
                qs = qs.filter(open_access=True)
            if cleaned['is_new']:
                qs = qs.filter(is_new=True)
            if cleaned['types']:
                qs = qs.filter(type__code__in=cleaned['types'])
            if cleaned['collections']:
                qs = qs.filter(collection__code__in=cleaned['collections'])
            if cleaned['disciplines']:
                qs = qs.filter(disciplines__code__in=cleaned['disciplines'])
        return qs.select_related('collection', 'type')

    def get_template_names(self):
        if self.sorting == 'name':
            return ['public/journal/journal_list_per_names.html', ]
        elif self.sorting == 'disciplines':
            return ['public/journal/journal_list_per_disciplines.html', ]


class JournalDetailView(
        SingleJournalMixin,
        ContentAccessCheckMixin,
        ContributorsMixin,
        DetailView,
):
    """
    Displays a journal.
    """
    context_object_name = 'journal'
    model = Journal
    template_name = 'public/journal/journal_detail.html'

    def get_context_data(self, **kwargs):
        context = super(JournalDetailView, self).get_context_data(**kwargs)

        # Fetches the JournalInformation instance associated to the current journal
        try:
            journal_info = self.object.information
            context['journal_info'] = journal_info
            # Generate cache keys based on journal info's directors and editors so that the cache
            # is not used when a director or editor is added (or removed).
            context['directors_cache_key'] = qs_cache_key(journal_info.get_directors())
            context['editors_cache_key'] = qs_cache_key(journal_info.get_editors())
        except ObjectDoesNotExist:
            journal_info = None
            # If the journal does not have a journal info, simulate one so the cache template tag
            # does have something to use to generate the cache key.
            context['journal_info'] = {'updated': None}
            context['directors_cache_key'] = None
            context['editors_cache_key'] = None

        # Notes
        context['notes'] = self.journal.erudit_object.get_notes(
            html=True,
            journal_pid=self.journal.pid,
        ).get(get_language(), []) if self.journal.is_in_fedora else []

        # Fetches the published issues and the latest issue associated with the current journal
        issues = [
            IssueAnnotator.annotate(issue, self) for issue in self.object.published_issues.all()]
        context['issues'] = issues
        current_issue = IssueAnnotator.annotate(self.object.current_issue, self)
        context['current_issue'] = current_issue
        if current_issue is not None and current_issue.is_in_fedora:
            titles = current_issue.erudit_object.get_journal_title()
            context['main_title'] = titles['main']
            context['paral_titles'] = titles['paral']
            context['journal_formatted_title'] = current_issue.journal_formatted_title
            context['meta_info_issue'] = current_issue
            # If we have a current issue, use its localidentifier for the cache key.
            context['primary_cache_key'] = current_issue.localidentifier
        else:
            # If the journal does not have any issue yet, simulate one so the cache template tag
            # does have something to use to generate the cache key.
            context['main_title'] = dict(
                title=self.object.name,
                subtitle=self.object.subtitle,
            )

            context['paral_titles'] = []

            context['journal_formatted_title'] = self.object.formatted_title

            context['meta_info_issue'] = {
                'localidentifier': None,
                'fedora_updated': None,
            }
            # If we don't have a current issue, use the journal code for the cache key.
            context['primary_cache_key'] = self.journal.code

        # Directors & editors.
        context['contributors'] = self.get_contributors(
            journal_info=journal_info,
            issue=current_issue,
        )

        # Generate a cache key based on the forced free access issues queryset so that the cache is
        # invalidated when the queryset changes.
        free_access_issues = self.object.published_issues.order_by('pk').filter(
            force_free_access=True,
        )
        context['free_access_cache_key'] = qs_cache_key(free_access_issues)

        # A list of Fedora objects' pids to which this view's templates cache keys will
        # be associated. For each pid in this list, EruditCache will add this view's
        # templates cache keys to a Redis tag with `tag:<pid>` as the tag key.
        context['cache_pids'] = [
            self.object.pid,
        ] + [issue.pid for issue in issues]

        return context


class JournalAuthorsListView(SingleJournalMixin, ContributorsMixin, TemplateView):
    """
    Displays a list of authors associated with a specific journal.
    """
    template_name = 'public/journal/journal_authors_list.html'

    def get(self, request, *args, **kwargs):
        self.init_get_parameters(request)
        return super(JournalAuthorsListView, self).get(request, *args, **kwargs)

    def init_get_parameters(self, request):
        """ Initializes and verify GET parameters. """
        self.letter = request.GET.get('letter', None)
        try:
            assert self.letter is not None
            self.letter = str(self.letter).upper()
            assert len(self.letter) == 1 and 'A' <= self.letter <= 'Z'
        except AssertionError:
            self.letter = None
        self.article_type = request.GET.get('article_type', None)
        try:
            assert self.article_type in (Article.ARTICLE_DEFAULT, Article.ARTICLE_REPORT)
        except AssertionError:
            self.article_type = None

    def get_solr_article_type(self):
        if not self.has_multiple_article_types:
            return None
        if self.article_type == 'compterendu':
            return 'Compte rendu'
        elif self.article_type == 'article':
            return 'Article'
        else:
            return None

    def get_authors_dict(self):
        if self.letter is None:
            for letter, exists in self.letters_exists.items():
                if exists:
                    self.letter = letter
                    break
            else:
                return {}
        return solr.get_journal_authors_dict(
            self.journal.solr_code, self.letter, self.get_solr_article_type())

    @cached_property
    def has_multiple_article_types(self):
        return len(solr.get_journal_authors_article_types(self.journal.solr_code)) > 1

    @cached_property
    def letters_exists(self):
        """ Returns an ordered dict containing the number of authors for each letter. """
        letters = solr.get_journal_authors_letters(
            self.journal.solr_code, self.get_solr_article_type())
        all_letters = ascii_uppercase
        return OrderedDict((letter, letter in letters) for letter in all_letters)

    def get_context_data(self, **kwargs):
        context = super(JournalAuthorsListView, self).get_context_data(**kwargs)
        context['authors_dicts'] = self.get_authors_dict()
        context['journal'] = self.journal
        context['letter'] = self.letter
        context['article_type'] = self.article_type
        context['letters_exists'] = self.letters_exists
        context['current_issue'] = self.journal.current_issue
        if context['current_issue'] is not None:
            context['meta_info_issue'] = context['current_issue']
            # If we have a current issue, use its localidentifier for the cache key.
            context['primary_cache_key'] = context['current_issue'].localidentifier
            context['journal_formatted_title'] = context['current_issue'].journal_formatted_title
        else:
            # If the journal does not have any issue yet, simulate one so the cache template tag
            # does have something to use to generate the cache key.
            context['meta_info_issue'] = {
                'localidentifier': None,
                'fedora_updated': None,
            }
            # If we don't have a current issue, use the journal code for the cache key.
            context['primary_cache_key'] = self.journal.code
            context['journal_formatted_title'] = self.journal.formatted_title

        # Fetches the JournalInformation instance associated to the current journal
        try:
            journal_info = self.journal.information
            context['journal_info'] = journal_info
            # Generate cache keys based on journal info's directors and editors so that the cache
            # is not used when a director or editor is added (or removed).
            context['directors_cache_key'] = qs_cache_key(journal_info.get_directors())
            context['editors_cache_key'] = qs_cache_key(journal_info.get_editors())
        except ObjectDoesNotExist:
            journal_info = None
            context['directors_cache_key'] = None
            context['editors_cache_key'] = None

        # Directors & editors.
        context['contributors'] = self.get_contributors(
            journal_info=journal_info,
            issue=context['current_issue'],
        )

        return context


class JournalRawLogoView(SingleJournalMixin, FedoraFileDatastreamView):
    """
    Returns the image file associated with a Journal instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'logo'
    fedora_object_class = JournalDigitalObject
    model = Journal


class IssueDetailView(
        FallbackObjectViewMixin,
        ContentAccessCheckMixin,
        PrepublicationTokenRequiredMixin,
        ContributorsMixin,
        DetailView):
    """
    Displays an Issue instance.
    """
    context_object_name = 'issue'
    model = Issue
    template_name = 'public/journal/issue_detail.html'

    def __init__(self):
        super().__init__()
        self.object = None

    def dispatch(self, *args, **kwargs):
        object = self.get_object()
        if object.external_url:
            return redirect(self.object.external_url)
        return super().dispatch(*args, **kwargs)

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        obj = self.get_object()
        if not obj.is_published:
            querystring_dict['ticket'] = obj.prepublication_ticket
        return querystring_dict

    def get_fallback_url_format(self):
        obj = self.get_object()
        if obj.journal.type and obj.journal.type.code == 'S':
            return "/revue/{code}/{year}/v{volume}/n{number}/index.html"
        else:
            return "/culture/{journal_li}/{issue_li}/index.html"

    def get_fallback_url_format_kwargs(self):
        issue = self.get_object()
        if issue.journal.type and issue.journal.type.code == 'S':
            return {
                'code': issue.journal.code,
                'year': issue.year,
                'volume': issue.volume,
                'number': issue.number,
            }
        else:
            return {
                'journal_li': issue.journal.localidentifier,
                'issue_li': issue.localidentifier,
            }

    def get_object(self, queryset=None):
        if self.object is not None:
            return self.object

        qs = Issue.internal_objects.select_related(
            'journal',
            'journal__collection',
            'journal__information',
            'journal__type'
        ).prefetch_related(
            'journal__disciplines'
        )

        try:
            self.object = qs.get(localidentifier=self.kwargs['localidentifier'])
        except Issue.DoesNotExist:
            try:
                self.object = Issue.from_fedora_ids(
                    self.kwargs['journal_code'],
                    self.kwargs['localidentifier'],
                )
            except Issue.DoesNotExist:
                raise Http404()

        return self.object

    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        context['journal'] = self.object.journal

        # Use the issue localidentifier for the cache key.
        context['primary_cache_key'] = self.object.localidentifier

        # Back issues should be ordered by year, volume & number, and should not include current one
        context['back_issues'] = context['journal'].published_issues.order_by(
            '-year',
            '-volume',
            '-number',
        ).exclude(
            localidentifier=self.object.localidentifier,
        )[:4]

        try:
            context['journal_info'] = self.object.journal.information
        except ObjectDoesNotExist:
            pass

        titles = self.object.erudit_object.get_journal_title()
        context['main_title'] = titles['main']
        context['paral_titles'] = titles['paral']
        context['journal_formatted_title'] = self.object.journal_formatted_title

        context['meta_info_issue'] = self.object
        guest_editors = self.object.erudit_object.get_redacteurchef(
            typerc="invite",
            formatted=True,
            idrefs=[]
        )

        context["notegens"] = self.object.erudit_object.get_notegens_edito(html=True)
        context["guest_editors"] = None if len(guest_editors) == 0 else guest_editors
        context['themes'] = self.object.erudit_object.get_themes(formatted=True, html=True)
        articles = list(self.object.get_articles_from_fedora())
        context['articles_per_section'] = self.generate_sections_tree(articles)
        context['articles'] = articles
        # If this is a cultural journal, we need the URL for the issue reader.
        if self.object.journal.is_cultural():
            context['reader_url'] = reverse('public:journal:issue_reader', kwargs={
                'journal_code': self.object.journal.code,
                'issue_slug': self.object.volume_slug,
                'localidentifier': self.object.localidentifier,
            })
        if not self.object.is_published:
            context['ticket'] = self.object.prepublication_ticket

        # Directors & editors.
        context['contributors'] = self.get_contributors(
            issue=self.object
        )

        # Generate a cache key based on the list of articles so that the cache is not used when a
        # new article is added (or removed).
        context['articles_cache_key'] = ','.join([article.localidentifier for article in articles])

        # We don't need the directors & editors cache keys because in the context of an issue we
        # are getting the directors & editors from the XML.
        context['directors_cache_key'] = None
        context['editors_cache_key'] = None

        # A list of Fedora objects' pids to which this view's templates cache keys will
        # be associated. For each pid in this list, EruditCache will add this view's
        # templates cache keys to a Redis tag with `tag:<pid>` as the tag key.
        context['cache_pids'] = [
            self.object.journal.pid,
            self.object.pid,
        ] + [article.pid for article in articles]

        return context

    def generate_sections_tree(self, articles, title=None, title_paral=None, level=0):
        sections_tree = {
            'groups': [],
            'level': level,
            'titles': {
                'main': title,
                'paral': title_paral
            },
            'type': 'subsection'
        }

        if level == 3:
            sections_tree['groups'].append({
                'type': 'objects',
                'objects': articles,
                'level': level
            })
            return sections_tree

        for title, articles in groupby(
            articles, lambda a: getattr(a, 'section_title_' + str(level + 1))
        ):
            articles = list(articles)
            if title is None:
                sections_tree['groups'].append({
                    'type': 'objects',
                    'objects': articles,
                    'level': level,
                })
            else:
                title_paral = getattr(articles[0], 'section_title_' + str(level + 1) + '_paral')
                # liberuditarticle returns an `odict_value()` wrapper around the list. We just want
                # to make sure that this wrapper doesn't cause problems down the line. Force list.
                title_paral = list(title_paral)
                sub_tree = self.generate_sections_tree(
                    articles, level=level + 1,
                    title=title,
                    title_paral=title_paral,
                )
                notegens = [
                    notegen for notegen in articles[0].get_notegens() if
                    notegen['scope'] == 'surtitre' and level == 0 or
                    notegen['scope'] == 'surtitre2' and level == 1
                ]
                sub_tree.update({'notegens': notegens})
                sections_tree['groups'].append(sub_tree)
        return sections_tree


class IssueRawCoverpageView(FedoraFileDatastreamView):
    """
    Returns the image file associated with an Issue instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'coverpage'
    fedora_object_class = PublicationDigitalObject
    model = Issue

    def get_object(self):
        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])


class IssueRawCoverpageHDView(FedoraFileDatastreamView):
    """
    Returns the image file associated with an Issue instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'coverpage_hd'
    fedora_object_class = PublicationDigitalObject
    model = Issue

    def get_object(self):
        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])


class IssueReaderView(
        ContentAccessCheckMixin,
        PrepublicationTokenRequiredMixin,
        DetailView):
    """
    Display the issue reader.
    """
    model = Issue
    template_name = 'public/journal/issue_reader.html'
    context_object_name = 'issue'

    def get_object(self, queryset=None):
        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = self.get_object()
        # Raise 404 if journal is not cultural.
        if not issue.journal.is_cultural():
            raise Http404()
        pages_ds = issue.fedora_object.getDatastreamObject('PAGES')
        pages = et.fromstring(pages_ds.content.serialize())
        context['num_leafs'] = pages.get('nb')
        context['page_width'] = pages.get('imageWidth')
        context['page_height'] = pages.get('imageHeight')
        context['issue_url'] = reverse('public:journal:issue_detail', kwargs={
            'journal_code': issue.journal.code,
            'issue_slug': issue.volume_slug,
            'localidentifier': issue.localidentifier,
        })
        if not issue.is_published:
            context['ticket'] = issue.prepublication_ticket
        return context


class IssueReaderPageView(
        ContentAccessCheckMixin,
        PrepublicationTokenRequiredMixin,
        FedoraFileDatastreamView):
    """
    Display a page from an issue.
    """
    model = Issue
    content_type = 'image/jpeg'
    fedora_object_class = PageDigitalObject
    datastream_name = 'image'

    def get_object(self):
        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])

    def get_fedora_object_pid(self):
        issue = self.get_object()
        return '{}.p{}'.format(issue.pid, self.kwargs['page'])

    def get(self, request, *args, **kwargs):
        issue = self.get_object()
        # If the user does not have access to the issue, we only grant access to the 5 first pages.
        if issue.is_published and not self.content_access_granted and int(kwargs['page']) > 5:
            return redirect(static('img/bookreader/restriction.jpg'))
        return super().get(request, *args, **kwargs)


class IssueXmlView(
        ContentAccessCheckMixin,
        PrepublicationTokenRequiredMixin,
        FedoraFileDatastreamView,
        DetailView):
    """ Displays an Issue raw XML. """
    content_type = 'application/xml'
    datastream_name = 'summary'
    fedora_object_class = PublicationDigitalObject

    def get_object(self, queryset=None):
        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])

    def get_datastream_content(self, fedora_object):
        return fedora_object.xml_content


class BaseArticleDetailView(
    ArticleAccessLogMixin,
    FallbackObjectViewMixin,
    ContentAccessCheckMixin,
    SingleArticleWithScholarMetadataMixin,
    ArticleViewMetricCaptureMixin,
    PrepublicationTokenRequiredMixin,
    DetailView,
):
    context_object_name = 'article'
    model = Article
    tracking_view_type = 'html'
    page_title_suffix = None
    display_full_article = True
    display_abstracts = True
    display_biblio = True
    display_full_toc = False

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # If for some reason we try to access an external article, we should be redirected to the
        # external URL.
        if obj.is_external:
            return HttpResponsePermanentRedirect(obj.url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseArticleDetailView, self).get_context_data(**kwargs)

        context['page_title_suffix'] = self.page_title_suffix
        context['display_full_article'] = self.display_full_article
        context['display_abstracts'] = self.display_abstracts
        context['display_biblio'] = self.display_biblio
        context['display_full_toc'] = self.display_full_toc

        try:
            # Abstracts and keywords without HTML for metatags.
            context['meta_abstracts'] = self.object.erudit_object.get_abstracts(html=False)
            context['meta_keywords'] = self.object.erudit_object.get_keywords(html=False)
            # All titles for an article
            context['titles'] = self.object.erudit_object.get_titles()
        except ObjectDoesNotExist:
            pass

        # Get all article from associated Issue
        current_article = context.get(self.context_object_name)
        issue = current_article.issue

        # Pick the previous article and the next article
        previous_article, next_article = issue.get_previous_and_next_articles(
            current_article.localidentifier
        )
        context.update({
            'previous_article': previous_article,
            'next_article': next_article
        })

        context['in_citation_list'] = self.object.solr_id in self.request.saved_citations

        # This prefix is needed to generate media URLs in the XSD. We need to generate a valid
        # media URL and then remove the media_localid part to get the prefix only.
        url = reverse('public:journal:article_media', kwargs={
            'journal_code': issue.journal.code,
            'issue_slug': issue.volume_slug,
            'issue_localid': issue.localidentifier,
            'localid': current_article.localidentifier,
            'media_localid': 'x',  # that last 'x' will be removed.
        })
        context['media_url_prefix'] = url[:-1]

        if not issue.is_published:
            context['ticket'] = issue.prepublication_ticket

        context['render_xml_content'] = functools.partial(
            self.render_xml_content,
            context=context,
        )
        context['related_articles'] = functools.partial(
            self.get_related_articles,
            current_article=current_article,
        )
        context['active_campaign'] = Campaign.objects.active_campaign()

        # A list of Fedora objects' pids to which this view's templates cache keys will
        # be associated. For each pid in this list, EruditCache will add this view's
        # templates cache keys to a Redis tag with `tag:<pid>` as the tag key.

        previous_article_cache_key = None
        next_article_cache_key = None
        if previous_article:
            previous_article_cache_key =\
                f"{current_article.issue.pid}.{previous_article.localidentifier}"
        if next_article:
            next_article_cache_key = f"{current_article.issue.pid}.{next_article.localidentifier}"

        context['cache_pids'] = [
            current_article.issue.journal.pid,
            current_article.issue.pid,
            current_article.pid,
        ] + [
            cache_key
            for cache_key in (previous_article_cache_key, next_article_cache_key)
            if cache_key is not None
        ]

        return context

    def get_related_articles(self, current_article: Article) -> List[Article]:
        related_candidates = self.solr_data.get_journal_related_articles(
            current_article.issue.journal.code, current_article.localidentifier,
        )
        # return 4 randomly — at most
        random.shuffle(related_candidates)
        related_articles = []
        # calls to Article.from_solr_object are expensive, so create only selected articles
        for candidate in related_candidates:
            if len(related_articles) == 4:
                break
            try:
                related_articles.append(Article.from_solr_object(candidate))
            except Article.DoesNotExist:
                # This might happen for UNB articles with ID mismatch between Solr & Fedora.
                pass
        return related_articles

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(BaseArticleDetailView, self).dispatch(*args, **kwargs)

    def render_xml_content(self, context):
        """ Renders the given article instance as HTML. """

        article = self.get_object()
        context['is_of_type_roc'] = article.erudit_object.is_of_type_roc
        if 'article' not in context:
            context['article'] = article

        context['pdf_exists'] = article.has_pdf

        if context['pdf_exists'] and not article.abstracts:
            if context['content_access_granted']:
                context['can_display_first_pdf_page'] = True
            else:
                context['can_display_first_pdf_page'] = article.can_display_first_pdf_page

        # Renders the templates corresponding to the XSL stylesheet that
        # will allow us to convert ERUDITXSD300 articles to HTML
        xsl_template = loader.get_template('public/journal/eruditxsd300_to_html.xsl')
        xsl = xsl_template.render(context=context, request=self.request)

        # Performs the XSLT transformation
        lxsl = et.parse(io.BytesIO(force_bytes(xsl)))
        html_transform = et.XSLT(lxsl)
        html_content = html_transform(article.erudit_object._dom)

        # Combine unicode characters (like "a") followed by a unicode combining character (like "˘")
        # by the unicode pre-combined version (like ă).
        html_content = unicodedata.normalize('NFC', str(html_content))

        return mark_safe(html_content)


class ArticleDetailView(BaseArticleDetailView):
    """
    Displays an Article page.
    """
    fallback_url_format = "/revue/{code}/{year}/v{volume}/n{number}/{article_pid}.html"
    template_name = 'public/journal/article_detail.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        obj = self.get_object()
        if not obj.issue.is_published:
            querystring_dict['ticket'] = obj.issue.prepublication_ticket
        return querystring_dict

    def get_fallback_url_format(self):
        obj = self.get_object()
        if obj.issue.journal.type and obj.issue.journal.type.code == 'S':
            return "/revue/{code}/{year}/v{volume}/n{number}/{article_li}.html"
        else:
            return "/culture/{journal_li}/{issue_li}/{article_li}.html"

    def get_fallback_url_format_kwargs(self):
        obj = self.get_object()
        if obj.issue.journal.type and obj.issue.journal.type.code == 'S':
            return {
                'code': obj.issue.journal.code,
                'year': obj.issue.year,
                'volume': obj.issue.volume,
                'number': obj.issue.number,
                'article_li': obj.localidentifier,
            }
        else:
            return {
                'journal_li': obj.issue.journal.localidentifier,
                'issue_li': obj.issue.localidentifier,
                'article_li': obj.localidentifier
            }

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        if self.content_access_granted:
            if article.processing == Article.PROCESSING_FULL:
                return ArticleAccessType.html_full_view
            else:
                return ArticleAccessType.html_full_view_pdf_embedded
        else:
            if article.processing == Article.PROCESSING_FULL:
                return ArticleAccessType.html_preview
            else:
                return ArticleAccessType.html_preview_pdf_embedded


class ArticleSummaryView(BaseArticleDetailView):
    """
    Displays the summary of an Article instance.
    """
    template_name = 'public/journal/article_summary.html'
    page_title_suffix = _('Notice')
    display_full_article = False

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        if article.processing == Article.PROCESSING_FULL:
            return ArticleAccessType.html_preview
        else:
            return ArticleAccessType.html_preview_pdf_embedded


class ArticleBiblioView(BaseArticleDetailView):
    """
    Displays the bibliography of an Article instance.
    """
    template_name = 'public/journal/article_biblio.html'
    page_title_suffix = _('Bibliographie')
    display_full_article = False
    display_abstracts = False

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        return ArticleAccessType.html_biblio


class ArticleTocView(BaseArticleDetailView):
    """
    Displays the table of content of an Article instance.
    """
    template_name = 'public/journal/article_toc.html'
    page_title_suffix = _('Plan complet de l’article')
    display_full_article = False
    display_abstracts = False
    display_biblio = False
    display_full_toc = True

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        return ArticleAccessType.html_toc


class IdEruditArticleRedirectView(RedirectView, SolrDataMixin):
    pattern_name = 'public:journal:article_detail'

    def get_redirect_url(self, *args, **kwargs):
        fedora_ids = self.solr_data.get_fedora_ids(kwargs['localid'])
        if not fedora_ids:
            raise Http404()
        article = Article.from_fedora_ids(*fedora_ids)
        return reverse(self.pattern_name, args=[
            article.issue.journal.code, article.issue.volume_slug, article.issue.localidentifier,
            article.localidentifier, ])


class ArticleEnwCitationView(SingleArticleMixin, DetailView):
    """
    Returns the enw file of a specific article.
    """
    content_type = 'application/x-endnote-refer'
    context_object_name = 'article'
    template_name = 'public/journal/citation/article.enw'


class ArticleRisCitationView(SingleArticleMixin, DetailView):
    """
    Returns the ris file of a specific article.
    """
    content_type = 'application/x-research-info-systems'
    context_object_name = 'article'
    template_name = 'public/journal/citation/article.ris'


class ArticleBibCitationView(SingleArticleMixin, DetailView):
    """
    Returns the bib file of a specific article.
    """
    content_type = 'application/x-bibtex'
    context_object_name = 'article'
    template_name = 'public/journal/citation/article.bib'


class ArticleFormatDownloadView(
    ArticleAccessLogMixin,
    ArticleViewMetricCaptureMixin,
    ContentAccessCheckMixin,
    PermissionRequiredMixin,
    SingleArticleMixin,
    FedoraFileDatastreamView,
):

    def get_content(self):
        return self.get_object()

    def get_fedora_object_pid(self):
        article = self.get_content()
        return article.pid

    def get_permission_object(self):
        return self.get_content()

    def has_permission(self):
        obj = self.get_permission_object()
        return obj.publication_allowed and self.content_access_granted

    def handle_no_permission(self):
        return redirect('public:journal:article_detail', **self.kwargs)


class ArticleXmlView(ArticleFormatDownloadView):
    content_type = 'application/xml'
    datastream_name = 'erudit_xsd300'
    fedora_object_class = ArticleDigitalObject
    raise_exception = True
    tracking_view_type = 'xml'

    def get_datastream_content(self, fedora_object):
        return fedora_object.xml_content

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        return ArticleAccessType.xml_full_view


class ArticleRawPdfView(ArticleFormatDownloadView):
    """
    Returns the PDF file associated with an article.
    """
    content_type = 'application/pdf'
    datastream_name = 'pdf'
    fedora_object_class = ArticleDigitalObject
    raise_exception = True
    tracking_view_type = 'pdf'

    def write_datastream_content(self, response, content):
        coverpage = get_coverpage(self.get_object())
        response.content = add_coverpage_to_pdf(coverpage, content)

    def get_response_object(self, fedora_object):
        response = super(ArticleFormatDownloadView, self).get_response_object(fedora_object)
        if 'embed' not in self.request.GET:
            response['Content-Disposition'] = 'inline; filename={}.pdf'.format(
                self.kwargs['localid'])
        return response

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        if "embed" in self.request.GET:
            return ArticleAccessType.pdf_full_view_embedded
        else:
            return ArticleAccessType.pdf_full_view


class ArticleRawPdfFirstPageView(
    ArticleAccessLogMixin,
    ContentAccessCheckMixin,
    PermissionRequiredMixin,
    SingleArticleMixin,
    FedoraFileDatastreamView,
):
    """
    Returns the PDF file associated with an article.
    """
    content_type = 'application/pdf'
    datastream_name = 'pdf'
    fedora_object_class = ArticleDigitalObject
    raise_exception = True
    tracking_view_type = 'pdf'

    def get_content(self):
        return self.get_object()

    def get_fedora_object_pid(self):
        article = self.get_content()
        return article.pid

    def get_response_object(self, fedora_object):
        response = super(ArticleRawPdfFirstPageView, self).get_response_object(fedora_object)
        if 'embed' not in self.request.GET:
            response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
                self.kwargs['localid'])
        return response

    def get_permission_object(self):
        return self.get_content()

    def has_permission(self):
        obj = self.get_permission_object()
        return obj.publication_allowed and obj.can_display_first_pdf_page

    def write_datastream_content(self, response, content):
        response.content = get_pdf_first_page(content)

    def get_access_type(self) -> ArticleAccessType:
        article = self.get_object()
        if not article.publication_allowed:
            return ArticleAccessType.content_not_available
        if "embed" in self.request.GET:
            return ArticleAccessType.pdf_preview_embedded
        else:
            return ArticleAccessType.pdf_preview


class ArticleMediaView(SingleArticleMixin, FedoraFileDatastreamView):
    """
    Returns an image file embedded in the INFOIMG datastream.
    """
    datastream_name = 'content'
    fedora_object_class = MediaDigitalObject

    def get_fedora_object_pid(self):
        article = self.get_object()
        issue_pid = article.issue.pid
        return '{0}.{1}'.format(issue_pid, self.kwargs['media_localid'])

    def get_content_type(self, fedora_object):
        return str(fedora_object.content.mimetype)


@method_decorator(cache_page(settings.LONG_TTL), name='dispatch')
class GoogleScholarSubscribersView(TemplateView):
    content_type = 'text/xml'
    template_name = 'public/journal/scholar/subscribers.xml'

    def get_context_data(self, **kwargs):
        context = super(GoogleScholarSubscribersView, self).get_context_data(**kwargs)
        context['subscribers'] = {}
        subscriptions = JournalAccessSubscription.valid_objects.institutional().exclude(
            organisation__google_scholar_opt_out=True,
        ).prefetch_related(
            'organisation',
            Prefetch(
                'institutionipaddressrange_set',
                queryset=InstitutionIPAddressRange.objects.order_by('ip_start'),
                to_attr='ip_ranges',
            ),
        )
        for subscription in subscriptions:
            context['subscribers'][subscription.id] = {
                'institution': subscription.organisation.name,
                'ip_ranges': [
                    [ip_range.ip_start, ip_range.ip_end] for ip_range in
                    subscription.ip_ranges
                ],
            }
        return context


@method_decorator(cache_page(settings.LONG_TTL), name='dispatch')
class GoogleScholarSubscriberJournalsView(TemplateView):
    content_type = 'text/xml'
    template_name = 'public/journal/scholar/subscriber_journals.xml'

    def get_context_data(self, **kwargs):
        context = super(GoogleScholarSubscriberJournalsView, self).get_context_data(**kwargs)
        # If no subscription ID is provided we are looking for all journals with open access issues
        # and we set 'embargo' to True to include embargo information in the subscriber journals.
        if not kwargs.get('subscription_id'):
            context['journals'] = Journal.objects.filter(collection__is_main_collection=True)
            context['embargo'] = True
        else:
            # Otherwise, look for a valid institutional subscription and return its journals.
            try:
                subscription = JournalAccessSubscription.valid_objects.institutional().exclude(
                    organisation__google_scholar_opt_out=True,
                ).get(
                    pk=kwargs.get('subscription_id'),
                )
                context['journals'] = subscription.get_journals()
            # If no valid institutional subscription is found, return an empty list.
            except ObjectDoesNotExist:
                context['journals'] = []
        return context


class BaseExternalURLRedirectView(RedirectView):
    """ The base view to redirect for content that is hosted externally """

    model = None
    """ Model type for the considered redirection """

    permanent = False
    """ Whether the redirection is permanent or not """

    object_identifier_field = None
    """ The model field on which the lookup is performed """

    def get_collection(self, obj):
        raise NotImplementedError

    def get_redirect_url(self, *args, **kwargs):
        """ Return the redirect url for the object """

        filter_arguments = {
            self.object_identifier_field: kwargs[self.object_identifier_field],
        }

        obj = get_object_or_404(
            self.model.objects.filter(external_url__isnull=False),
            **filter_arguments
        )

        # Tracks the redirection
        metric(
            'erudit__journal__{0}_redirect'.format(self.model._meta.model_name.lower()),
            tags={'collection': self.get_collection(obj).code, },
            **{'localidentifier': obj.localidentifier, })
        return obj.external_url


class JournalExternalURLRedirectView(BaseExternalURLRedirectView):
    model = Journal
    object_identifier_field = 'code'

    def get_collection(self, obj):
        return obj.collection


class IssueExternalURLRedirectView(BaseExternalURLRedirectView):
    model = Issue
    object_identifier_field = 'localidentifier'

    def get_collection(self, obj):
        return obj.journal.collection


class JournalStatisticsView(PermissionRequiredMixin, TemplateView):
    template_name = 'public/journal/journal_statistics.html'
    permission_required = 'userspace.staff_access'

    def get_context_data(self, **kwargs):
        context = super(JournalStatisticsView, self).get_context_data(**kwargs)
        solr = pysolr.Solr(settings.SOLR_ROOT, timeout=settings.SOLR_TIMEOUT)
        search_kwargs = {
            'fq': [
                'Corpus_fac:(Article OR Culturel)',
                'Fonds_fac:(Érudit OR UNB)',
            ],
            'facet.field': [
                'Corpus_fac',
                'RevueAbr',
            ],
            'rows': 0,
        }
        results = solr.search('*:*', **search_kwargs)
        facet_fields = results.raw_response['facet_counts']['facet_fields']
        # Journal types.
        # Facet counts are returned as a flat list, alterning between the facet name and the facet
        # count, that's why we zip() the even and odd items from the list.
        context['journal_types'] = zip(
            facet_fields['Corpus_fac'][::2],
            facet_fields['Corpus_fac'][1::2],
        )
        # Journals.
        # Facet counts are returned as a flat list, alterning between the facet name and the facet
        # count, that's why we get the index of the journal legacy code and add 1 to get the count.
        context['journals'] = []
        journals = Journal.objects.filter(collection__is_main_collection=True).order_by('name')
        for journal in journals:
            if journal.legacy_code in facet_fields['RevueAbr']:
                index = facet_fields['RevueAbr'].index(journal.legacy_code)
                count = facet_fields['RevueAbr'][index + 1]
                context['journals'].append((journal.name, count))
            else:
                context['journals'].append((journal.name, 0))
        return context
