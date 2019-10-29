import datetime as dt
import os

import pytest
import unittest.mock

from django.http import Http404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.public.journal.viewmixins import SolrDataMixin
from base.test.factories import UserFactory
from erudit.test.factories import ArticleFactory, IssueFactory, JournalFactory, \
    JournalInformationFactory, ContributorFactory
from erudit.fedora import repository
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Issue
from erudit.test.domchange import SectionTitle
from erudit.test.solr import FakeSolrData
from apps.public.journal.views import (
    JournalDetailView,
    IssueDetailView,
    ArticleDetailView,
    GoogleScholarSubscribersView,
    GoogleScholarSubscriberJournalsView,
    JournalStatisticsView,
    IssueReaderView,
)
from core.subscription.test.factories import JournalAccessSubscriptionFactory

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')
pytestmark = pytest.mark.django_db


class TestJournalDetailView:

    @pytest.mark.parametrize('localidentifier, language, expected_notes', [
        ('journal1', 'fr', ['foobar']),
        ('journal1', 'en', ['foobaz']),
        # Should not crash if the journal is not in fedora.
        (None, 'fr', []),
    ])
    def test_get_context_data_with_notes(self, localidentifier, language, expected_notes):
        view = JournalDetailView()
        view.object = unittest.mock.MagicMock()
        view.request = unittest.mock.MagicMock()
        view.kwargs = unittest.mock.MagicMock()
        view.journal = JournalFactory(
            localidentifier=localidentifier,
            notes=[
                {'langue': 'fr', 'content': 'foobar'},
                {'langue': 'en', 'content': 'foobaz'}
            ],
        )
        with override_settings(LANGUAGE_CODE=language):
            context = view.get_context_data()
            assert context['notes'] == expected_notes

    def test_contributors(self):
        issue = IssueFactory()
        url = reverse('public:journal:journal_detail', kwargs={'code': issue.journal.code})

        # No contributors in journal_info, issue's contributors should be displayed.
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/images1102374.xml', 'rb').read(),
        )
        html = Client().get(url).content.decode()
        assert 'Claude Racine' in html
        assert 'Marie-Claude Loiselle (Rédactrice en chef)' in html
        assert 'Foo (Bar)' not in html

        # There's a director in journal_info, issue's contributors should not be displayed.
        journal_info = JournalInformationFactory(journal=issue.journal)
        journal_info.editorial_leaders.add(
            ContributorFactory(
                type='D',
                name='Foo',
                role='Bar',
                journal_information=journal_info,
            )
        )
        html = Client().get(url).content.decode()
        assert 'Claude Racine (Éditeur)' not in html
        assert 'Isabelle Richer (Rédactrice adjointe)' not in html
        assert 'Foo (Bar)' in html

    def test_available_since_when_issues_are_not_produced_in_the_same_order_as_their_published_date(self):
        journal = JournalFactory()
        issue_1 = IssueFactory(journal=journal, date_published=dt.date(2019, 1, 1))
        issue_2 = IssueFactory(journal=journal, date_published=dt.date(2015, 1, 1))
        issue_3 = IssueFactory(journal=journal, date_published=dt.date(2017, 1, 1))
        url = reverse('public:journal:journal_detail', kwargs={
            'code': journal.code,
        })
        html = Client().get(url).content.decode()
        assert '<dt>Disponible dans Érudit depuis</dt>\n          <dd>2015</dd>' in html

    @pytest.mark.parametrize('subtitle', [
        ('bar'),
        (''),
        (None),
    ])
    def test_journal_with_no_issue_title_and_subtitle_display(self, subtitle):
        journal = JournalFactory(
            name='foo',
            subtitle=subtitle,
        )
        url = reverse('public:journal:journal_detail', kwargs={
            'code': journal.code,
        })
        html = Client().get(url).content.decode()
        assert '<span class="journal-title">foo</span>' in html
        if subtitle:
            assert '<span class="journal-subtitle">bar</span>' in html
        else:
            assert '<span class="journal-subtitle">None</span>' not in html

    def test_journal_note_with_html_link(self):
        issue = IssueFactory()
        repository.api.set_xml_for_pid(
            issue.journal.get_full_identifier(),
            open('tests/fixtures/journal/recma0448.xml', 'rb').read(),
        )
        url = reverse('public:journal:journal_detail', kwargs={
            'code': issue.journal.code,
        })
        html = Client().get(url).content.decode()
        assert 'Cette revue a cessé de publier ses numéros sur Érudit depuis 2016, vous pouvez consulter les numéros subséquents sur <a href="https://www.cairn.info/revue-recma.htm">Cairn</a>' in html


class TestJournalAuthorsListView:

    def test_do_not_crash_for_journal_with_no_issue(self):
        journal = JournalFactory()
        url = reverse('public:journal:journal_authors_list', kwargs={'code': journal.code})
        response = Client().get(url)
        assert response.status_code == 200


class TestIssueDetailSummary:
    def test_generate_sections_tree_with_scope_surtitre(self):
        view = IssueDetailView()
        article_1 = ArticleFactory(from_fixture='1059644ar')
        article_2 = ArticleFactory(from_fixture='1059645ar')
        article_3 = ArticleFactory(from_fixture='1059646ar')
        sections_tree = view.generate_sections_tree([article_1, article_2, article_3])
        assert sections_tree == {
            'level': 0,
            'type': 'subsection',
            'titles': {'main': None, 'paral': None},
            'groups': [{
                'level': 1,
                'type': 'subsection',
                'titles': {'main': 'La recherche qualitative aujourd’hui. 30 ans de diffusion et de réflexion', 'paral': []},
                'notegens': [{
                    'content': ['Sous la direction de Frédéric Deschenaux, Chantal Royer et Colette Baribeau'],
                    'scope': 'surtitre',
                    'type': 'edito',
                }],
                'groups': [{
                    'level': 2,
                    'type': 'subsection',
                    'titles': {'main': 'Introduction', 'paral': []},
                    'notegens': [],
                    'groups': [{
                        'level': 2,
                        'type': 'objects',
                        'objects': [article_1],
                    }],
                }, {
                    'level': 1,
                    'type': 'objects',
                    'objects': [article_2, article_3],
                }],
            }],
        }

    def test_can_generate_section_tree_with_contiguous_articles(self):
        view = IssueDetailView()
        article_1 = ArticleFactory()
        article_2 = ArticleFactory()
        article_3 = ArticleFactory(section_titles=[SectionTitle(1, False, "section 1")])
        sections_tree = view.generate_sections_tree([article_1, article_2, article_3])
        assert sections_tree == {
            'titles': {'paral': None, 'main': None},
            'level': 0,
            'groups': [
                {'objects': [article_1, article_2], 'type': 'objects', 'level': 0},
                {
                    'titles': {'paral': [], 'main': "section 1"},
                    'level': 1,
                    'groups': [{'objects': [article_3], 'type': 'objects', 'level': 1}],
                    'type': 'subsection',
                    'notegens': [],
                },
            ],
            'type': 'subsection',
        }

    def test_can_generate_section_tree_with_three_levels(self):
        view = IssueDetailView()
        article = ArticleFactory(section_titles=[
            SectionTitle(1, False, "section 1"),
            SectionTitle(2, False, "section 2"),
            SectionTitle(3, False, "section 3"),
        ])

        sections_tree = view.generate_sections_tree([article])
        assert sections_tree == {
            'type': 'subsection',
            'level': 0,
            'titles': {'paral': None, 'main': None},
            'groups': [{
                'type': 'subsection',
                'level': 1,
                'titles': {'paral': [], 'main': 'section 1'},
                'notegens': [],
                'groups': [{
                    'type': 'subsection',
                    'level': 2,
                    'titles': {'paral': [], 'main': 'section 2'},
                    'notegens': [],
                    'groups': [{
                        'type': 'subsection',
                        'level': 3,
                        'titles': {'paral': [], 'main': 'section 3'},
                        'groups': [
                            {'objects': [article], 'type': 'objects', 'level': 3},
                        ],
                        'notegens': [],
                    }]
                }]
            }]
        }

    def test_can_generate_section_tree_with_non_contiguous_articles(self):
        view = IssueDetailView()
        articles = [
            ArticleFactory(section_titles=[SectionTitle(1, False, "section 1")]),
            ArticleFactory(section_titles=[
                SectionTitle(1, False, "section 1"),
                SectionTitle(2, False, "section 1.1"),
            ]),
            ArticleFactory(section_titles=[SectionTitle(1, False, "section 1")]),
        ]

        sections_tree = view.generate_sections_tree(articles)
        assert sections_tree == {
            'type': 'subsection',
            'level': 0,
            'titles': {'paral': None, 'main': None},
            'groups': [
                {
                    'type': 'subsection',
                    'level': 1,
                    'titles': {
                        'paral': [], 'main': 'section 1'
                    },
                    'notegens': [],
                    'groups': [
                        {'type': 'objects', 'level': 1, 'objects': [articles[0]]},
                        {
                            'type': 'subsection', 'level': 2, 'titles': {'paral': [], 'main': 'section 1.1'},  # noqa
                            'groups': [{'type': 'objects', 'level': 2, 'objects': [articles[1]]}],
                            'notegens': [],
                        },
                        {
                            'type': 'objects', 'level': 1, 'objects': [articles[2]],
                        }
                    ]
                }
            ]
        }

    def test_can_generate_section_tree_with_notegens(self):
        view = IssueDetailView()
        articles = [
            ArticleFactory(
                section_titles=[
                    SectionTitle(1, False, "Section 1"),
                ],
                notegens=[
                    {'content': 'Note surtitre', 'scope': 'surtitre', 'type': 'edito'},
                ],
            ),
            ArticleFactory(
                section_titles=[
                    SectionTitle(1, False, "Section 1"),
                    SectionTitle(2, False, "Section 2"),
                ],
                notegens=[
                    {'content': 'Note surtitre2', 'scope': 'surtitre2', 'type': 'edito'},
                ],
            ),
        ]
        sections_tree = view.generate_sections_tree(articles)
        assert sections_tree == {
            'level': 0,
            'type': 'subsection',
            'titles': {'main': None, 'paral': None},
            'groups': [{
                'level': 1,
                'type': 'subsection',
                'titles': {'main': 'Section 1', 'paral': []},
                'notegens': [{
                    'content': ['Note surtitre'],
                    'scope': 'surtitre',
                    'type': 'edito',
                }],
                'groups': [{
                    'level': 1,
                    'objects': [articles[0]],
                    'type': 'objects',
                }, {
                    'level': 2,
                    'type': 'subsection',
                    'titles': {'main': 'Section 2', 'paral': []},
                    'notegens': [{
                        'content': ['Note surtitre2'],
                        'scope': 'surtitre2',
                        'type': 'edito',
                    }],
                    'groups': [{
                        'level': 2,
                        'objects': [articles[1]],
                        'type': 'objects',
                    }],
                }],
            }],
        }

    @unittest.mock.patch('erudit.fedora.modelmixins.cache')
    @pytest.mark.parametrize('is_published, expected_count', [
        # When an issue is not published, the only cache.get() call we should get is for the
        # journal. No cache.get() should be called for the issue or the articles.
        (False, 1),
        # When an issue is published, cache.get() should be called once for the journal, once for
        # the issue and once for each article.
        (True, 3),
    ])
    def test_issue_caching(self, mock_cache, is_published, expected_count):
        mock_cache.get.return_value = None

        article = ArticleFactory(issue__is_published=is_published)
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        mock_cache.get.reset_mock()

        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket,
        })
        assert mock_cache.get.call_count == expected_count

    def test_main_title_and_paral_title(self):
        article = ArticleFactory(
            from_fixture='1058197ar',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        # Check that there's only one space between the main title and the '/'.
        assert 'Inaugural Lecture of the FR Scott Professor&nbsp;/ Conférence inaugurale du Professeur FR Scott' in html

    def test_issue_detail_view_with_untitled_article(self):
        article = ArticleFactory(
            from_fixture='1042058ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__name='Revue',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<h6 class="bib-record__title">\n    \n    <a href="/fr/revues/journal/2000-issue/article/"\n    \n    title="Lire l\'article">\n    [Article sans titre]\n    </a>\n  </h6>' in html

    def test_article_authors_are_not_displayed_with_suffixes(self):
        article = ArticleFactory(
            from_fixture='1058611ar',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that authors' suffixes are not displayed on the issue detail view.
        assert '<p class="bib-record__authors col-sm-9">\n      Mélissa Beaudoin, Stéphane Potvin, Laura Dellazizzo, Maëlle Surprenant, Alain Lesage, Alain Vanasse, André Ngamini-Ngui et Alexandre Dumais\n    </p>' in html

    @pytest.mark.parametrize('journal_type', [
        ('S'),
        ('C'),
    ])
    @pytest.mark.parametrize('is_published', [
        (True),
        (False),
    ])
    def test_issue_reader_url_in_context_for_cultural_journal_issues(self, journal_type, is_published):
        issue = IssueFactory(
            is_published=is_published,
            year='2000',
            localidentifier='issue',
            journal__code='journal',
            journal__type_code=journal_type,
        )
        issue.is_prepublication_ticket_valid = unittest.mock.MagicMock()
        view = IssueDetailView()
        view.object = issue
        view.request = unittest.mock.MagicMock()
        context = view.get_context_data()
        if journal_type == 'C':
            assert context['reader_url'] == '/fr/revues/journal/2000-issue/feuilletage/'
            if not is_published:
                assert context['ticket'] == issue.prepublication_ticket
        else:
            assert 'reader_url' not in context


class TestIssueReaderView:

    @pytest.mark.parametrize('journal_type', [
        ('S'),
        ('C'),
    ])
    @pytest.mark.parametrize('is_published', [
        (True),
        (False),
    ])
    def test_get_context_data(self, journal_type, is_published):
        issue = IssueFactory(
            is_published=is_published,
            year='2000',
            localidentifier='issue',
            journal__code='journal',
            journal__type_code=journal_type,
        )
        issue.is_prepublication_ticket_valid = unittest.mock.MagicMock()
        view = IssueReaderView()
        view.object = issue
        view.get_object = unittest.mock.MagicMock(return_value=issue)
        view.request = unittest.mock.MagicMock()
        view.kwargs = unittest.mock.MagicMock()
        if journal_type == 'C':
            context = view.get_context_data()
            assert context['num_leafs'] == '80'
            assert context['page_width'] == '1350'
            assert context['page_height'] == '1800'
            assert context['issue_url'] == '/fr/revues/journal/2000-issue/'
            if not is_published:
                assert context['ticket'] == issue.prepublication_ticket
        else:
            with pytest.raises(Http404):
                context = view.get_context_data()


class TestIssueReaderPageView:

    @pytest.mark.parametrize('page, open_access, is_published, ticket, expected_status_code, expected_redirection', [
        # All pages should be accessible for open access published issues.
        ('1', True, True, False, 200, ''),
        ('6', True, True, False, 200, ''),
        # Only the 5 first pages should be accessible for embargoed published issues.
        ('1', False, True, False, 200, ''),
        ('6', False, True, False, 302, '/static/img/bookreader/restriction.jpg'),
        # All pages should be accessible for unpublished issues when a prepublication ticket is provided.
        ('1', True, False, True, 200, ''),
        ('6', True, False, True, 200, ''),
        ('1', False, False, True, 200, ''),
        ('6', False, False, True, 200, ''),
        # No pages should be accessible for unpublished issues when no prepublication ticket is provided.
        ('1', True, False, False, 302, '/fr/revues/journal/'),
        ('6', True, False, False, 302, '/fr/revues/journal/'),
        ('1', False, False, False, 302, '/fr/revues/journal/'),
        ('6', False, False, False, 302, '/fr/revues/journal/'),
    ])
    def test_issue_reader_page_view(self, page, open_access, is_published, ticket, expected_status_code, expected_redirection):
        issue = IssueFactory(
            is_published=is_published,
            journal__open_access=open_access,
            journal__code='journal',
        )
        url = reverse('public:journal:issue_reader_page', kwargs={
            'journal_code': issue.journal.code,
            'issue_slug': issue.volume_slug,
            'localidentifier': issue.localidentifier,
            'page': page,
        })
        response = Client().get(url, {
            'ticket': issue.prepublication_ticket if ticket else '',
        })
        assert response.status_code == expected_status_code
        if expected_redirection:
            assert response.url == expected_redirection


class TestIssueXmlView:

    @pytest.mark.parametrize('ticket', [
        True, False,
    ])
    @pytest.mark.parametrize('is_published', [
        True, False,
    ])
    def test_issue_raw_xml_view(self, is_published, ticket):
        issue = IssueFactory(
            is_published=is_published,
            journal__code='journal',
        )
        url = reverse('public:journal:issue_raw_xml', kwargs={
            'journal_code': issue.journal.code,
            'issue_slug': issue.volume_slug,
            'localidentifier': issue.localidentifier,
        })
        response = Client().get(url, {
            'ticket': issue.prepublication_ticket if ticket else '',
        }, follow=True)
        # The Issue XML view should be accessible if the issue is published or if a prepublication
        # ticket is provided.
        if is_published or ticket:
            with open('./tests/fixtures/issue/minimal.xml', mode='r') as xml:
                assert response.content.decode() in xml.read()
        # The Issue XML view should redirect to the journal detail view if the issue is not
        # published and a prepublication ticket is not provided.
        else:
            assert response.redirect_chain == [('/fr/revues/journal/', 302)]


@unittest.mock.patch.object(
    Issue,
    'erudit_object',
)
@unittest.mock.patch.object(
    ArticleDigitalObject,
    'erudit_xsd300',
    content=unittest.mock.MagicMock()
)
@unittest.mock.patch.object(
    ArticleDigitalObject,
    '_get_datastreams',
    return_value=['ERUDITXSD300', ]
)
@unittest.mock.patch.object(
    Issue,
    'has_coverpage',
    return_value=True
)
class TestRenderArticleTemplateTag:

    @pytest.fixture(autouse=True)
    def article_detail_solr_data(self, monkeypatch):
        monkeypatch.setattr(SolrDataMixin, 'solr_data', FakeSolrData())

    def mock_article_detail_view(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, fixture='article.xml'):
        """ Helper method to mock an article detail view from a given fixture."""
        with open(FIXTURE_ROOT + '/' + fixture, mode='r') as fp:
            xml = fp.read()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        article = ArticleFactory()
        view = ArticleDetailView()
        view.request = unittest.mock.MagicMock()
        view.object = article
        view.get_object = unittest.mock.MagicMock(return_value=article)
        context = view.get_context_data()

        # Run the XSL transformation.
        return view.render_xml_content(context)

    def test_can_transform_article_xml_to_html(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo)

        # Check
        assert ret is not None
        assert ret.startswith('<div xmlns:v="variables-node" class="article-wrapper">')

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    def test_can_transform_article_xml_to_html_when_pdf_exists(
            self, mock_pdf, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        # Setup
        fp = open(FIXTURE_ROOT + '/article.pdf', mode='rb')
        mock_pdf.exists = True
        mock_pdf.content = fp

        # Run
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo)

        # Check
        fp.close()
        assert ret is not None

    def test_html_tags_in_transformed_article_biblio_titles(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo)

        # Check that HTML tags in biblio titles are not stripped.
        assert '<h3 class="titre">H3 avec balise <strong>strong</strong>\n</h3>' in ret
        assert '<h4 class="titre">H4 avec balise <em>em</em>\n</h4>' in ret
        assert '<h5 class="titre">H5 avec balise <small>small</small>\n</h5>' in ret

    def test_footnotes_in_section_titles_not_in_toc(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

        # Check that footnotes in section titles are stripped when displayed in
        # table of content and not stripped when displayed as section titles.
        assert '<a href="#s1n1">Titre</a>' in ret
        assert '<h2>Titre<a href="#no1" id="re1no1" class="norenvoi" title="Note 1, avec espace entre deux marquages">[1]</a>\n</h2>' in ret

        assert '<a href="#s1n2"><strong>Titre gras</strong></a>' in ret
        assert '<h2><strong>Titre gras<a href="#no2" id="re1no2" class="norenvoi" title="Lien à encoder">[2]</a></strong></h2>' in ret

        assert '<a href="#s1n3"><em>Titre italique</em></a>' in ret
        assert '<h2><em>Titre italique<a href="#no3" id="re1no3" class="norenvoi" title="Lien déjà encodé">[3]</a></em></h2>' in ret

        assert '<a href="#s1n4"><span class="petitecap">Titre petitecap</span></a>' in ret
        assert '<h2><span class="petitecap">Titre petitecap<a href="#no4" id="re1no4" class="norenvoi" title="">[4]</a></span></h2>' in ret

    def test_space_between_two_tags(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

        # Check that the space is preserved between two tags.
        assert '<span class="petitecap">Note 1,</span> <em>avec espace entre deux marquages</em>' in ret

    def test_blockquote_between_two_spans(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

        # Check that the blockquote is displayed before the second paragraph.
        assert '<blockquote class="bloccitation ">\n<p class="alinea">Citation</p>\n<cite class="source">Source</cite>\n</blockquote>\n<p class="alinea">Paragraphe</p>' in ret

    def test_annexes_footnotes(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1035294ar.xml')

        # Check that annexes have an ID set.
        assert '<div id="an1" class="article-section-content" role="complementary">' in ret
        assert '<div id="an2" class="article-section-content" role="complementary">' in ret
        assert '<div id="an3" class="article-section-content" role="complementary">' in ret
        # Check that footnotes are linked to the annexes IDs.
        assert '<a href="#an1" id="" class="norenvoi" title="">[2]</a>' in ret
        assert '<a href="#an2" id="" class="norenvoi" title="">[ii]</a>' in ret
        assert '<a href="#an3" id="" class="norenvoi" title="">[**]</a>' in ret
        # Check that footnotes are not wrapped in <sup>.
        assert '<sup><a href="#an1" id="" class="norenvoi" title="">[2]</a></sup>' not in ret
        assert '<sup><a href="#an2" id="" class="norenvoi" title="">[ii]</a></sup>' not in ret
        assert '<sup><a href="#an3" id="" class="norenvoi" title="">[**]</a></sup>' not in ret

    def test_space_between_keywords_and_colon(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1055726ar.xml')

        # Check that a space is present before the colon in French, but not in the other languages.
        assert 'Mots-clés :' in ret
        assert 'Keywords:' in ret
        assert 'Palabras clave:' in ret

    def test_article_titles_css_class(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1055651ar.xml')
        # A normal title should not have any class.
        assert '<h2>La synthèse hoguettienne</h2>' in ret
        # A special character title should have the 'special' class.
        assert '<h2 class="special">*</h2>' in ret
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1055648ar.xml')
        # An empty title should have the 'special' and 'empty' classes and should be empty.
        assert '<h2 class="special empty"></h2>' in ret

    def test_volumaison_punctuation(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053504ar.xml')
        # There should be an hyphen between multiple months and no coma between month and year.
        assert '<p class="refpapier"><span class="volumaison"><span class="nonumero">Numéro 179</span>, Janvier–Avril 2018</span>, p. 1–2</p>' in ret

    def test_separator_between_sections_in_different_languages(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1046558ar.xml')
        # There should not be a separator before the first section.
        assert '<hr>\n<section id="s1n1"><div class="para" id="pa1">' not in ret
        # There should be a separator before sections in different languages.
        assert '<hr>\n<section id="s1n2"><div class="para" id="pa11">' in ret
        assert '<hr>\n<section id="s1n3"><div class="para" id="pa21">' in ret

    def test_multilingual_titreparal_and_sstitreparal_order(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1058157ar.xml')
        # Check that titreparal and sstitreparal are in the right order.
        assert '<h1 class="doc-head__title">\n<span class="titre">Introduction au dossier spécial</span><span class="sstitre">À la découverte du lien organisationnel : avez-vous lu A. O. Hirschman ?</span><span class="titreparal">Introduction to the special section</span><span class="sstitreparal">Exploring the Organizational Link: Have You Read A. O.\n        Hirschman?</span><span class="titreparal">Introducción Dossier Especial</span><span class="sstitreparal">Descubriendo las relaciones organizativas: ¿leyó a A.O.\n        Hirschman?</span>\n</h1>' in ret


class TestGoogleScholarSubscribersView:

    @pytest.mark.parametrize('google_scholar_opt_out, expected_subscribers', [
        (False, {
            1: {
                'institution': 'foo',
                'ip_ranges': [
                    ['0.0.0.0', '255.255.255.255'],
                ],
            },
        }),
        (True, {}),
    ])
    def test_google_scholar_subscribers(self, google_scholar_opt_out, expected_subscribers):
        JournalAccessSubscriptionFactory(
            pk=1,
            post__ip_start='0.0.0.0',
            post__ip_end='255.255.255.255',
            post__valid=True,
            organisation__name='foo',
            organisation__google_scholar_opt_out=google_scholar_opt_out,
        )
        view = GoogleScholarSubscribersView()
        context = view.get_context_data()
        assert context.get('subscribers') == expected_subscribers


class TestGoogleScholarSubscriberJournalsView:

    @pytest.mark.parametrize('google_scholar_opt_out, subscription_id, expected_journal_ids', [
        (False, '1', ['journal_1']),
        (False, '', ['journal_1', 'journal_2']),
        (True, '1', []),
    ])
    def test_google_scholar_subscriber_journals(self, google_scholar_opt_out, subscription_id, expected_journal_ids):
        journal_1 = JournalFactory(localidentifier='journal_1')
        journal_2 = JournalFactory(localidentifier='journal_2')
        JournalAccessSubscriptionFactory(
            pk=1,
            post__journals=[journal_1],
            organisation__google_scholar_opt_out=google_scholar_opt_out,
        )
        view = GoogleScholarSubscriberJournalsView()
        context = view.get_context_data(subscription_id=subscription_id)
        assert [journal.localidentifier for journal in context.get('journals')] == expected_journal_ids


class TestJournalStatisticsView:

    @pytest.mark.parametrize('is_staff, is_superuser, has_permission', [
        (True, True, True),
        (True, False, True),
        (False, True, True),
        (False, False, False),
    ])
    def test_journal_statistics_view_access(self, is_staff, is_superuser, has_permission):
        view = JournalStatisticsView()
        view.request = unittest.mock.MagicMock()
        view.request.user = UserFactory(
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        assert view.has_permission() == has_permission
