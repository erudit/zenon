import os
import pytest
import unittest.mock

from django.http import Http404

from erudit.test.factories import JournalFactory, IssueFactory
from apps.public.journal.views_compat import IssueDetailRedirectView


pytestmark = pytest.mark.django_db


class TestIssueDetailRedirectView:

    @pytest.mark.parametrize('localidentifier, ticket, expected_url', [
        ('issue-1', '', '/fr/revues/journal-1/2001-v1-n1-issue-1/'),
        # Ticket in request should be added to URL.
        ('issue-1', 'foobar', '/fr/revues/journal-1/2001-v1-n1-issue-1/?ticket=foobar'),
        # Nonexistent localidentifier should raise 404.
        ('issue-404', '', False),
    ])
    def test_get_redirect_url_with_id_in_request(self, localidentifier, ticket, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            volume='1',
            number='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        view.request.GET = {'id': localidentifier, 'ticket': ticket}
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1')
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1')

    @pytest.mark.parametrize('localidentifier, expected_url', [
        ('issue-1', '/fr/revues/journal-1/2001-v1-n1-issue-1/'),
        # Nonexistent localidentifier should raise 404.
        ('issue-404', False),
    ])
    def test_get_redirect_url_with_localidentifier(self, localidentifier, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            volume='1',
            number='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', localidentifier=localidentifier)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', localidentifier=localidentifier)

    @pytest.mark.parametrize('year, volume, number, expected_url', [
        ('2001', '1', '1', '/fr/revues/journal-1/2001-v1-n1-issue-1/'),
        # If year, volume or number is omitted, the right issue should still be found.
        ('', '1', '1', '/fr/revues/journal-1/2001-v1-n1-issue-1/'),
        ('2001', '', '1', '/fr/revues/journal-1/2001-v1-n1-issue-1/'),
        ('2001', '1', '', '/fr/revues/journal-1/2001-v1-n1-issue-1/'),
        # Wrong year, volume or number should raise 404.
        ('1999', '1', '1', False),
        ('2001', '0', '1', False),
        ('2001', '1', '0', False),
    ])
    def test_get_redirect_url_with_year_volume_and_number(self, year, volume, number, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            volume='1',
            number='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', year=year, v=volume, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', year=year, v=volume, n=number)

    @pytest.mark.parametrize('year, volume, number, expected_url', [
        # Issue that covers several years should be found by any year that is covered.
        ('2001', '1-2', '3-4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2002', '1-2', '3-4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2001', '3', '1', '/fr/revues/journal-1/2002-v3-n1-issue-2/'),
        ('2002', '3', '1', '/fr/revues/journal-1/2002-v3-n1-issue-2/'),
        # Issues with multiple volumes should be found by any volume.
        ('2001', '1-2', '3-4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2001', '1', '3-4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2001', '2', '3-4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2001', '3-4', '1', '/fr/revues/journal-1/2002-v3-n1-issue-2/'),
        ('2001', '3', '1', '/fr/revues/journal-1/2002-v3-n1-issue-2/'),
        # Issues with multiple numbers should be found by any number.
        ('2002', '1-2', '3-4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2002', '1-2', '3', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2002', '1-2', '4', '/fr/revues/journal-1/2001-v1-2-n3-4-issue-1/'),
        ('2002', '3', '1-2', '/fr/revues/journal-1/2002-v3-n1-issue-2/'),
        ('2002', '3', '1', '/fr/revues/journal-1/2002-v3-n1-issue-2/'),
    ])
    def test_get_redirect_url_with_multiple_year_volume_and_number(self, year, volume, number, expected_url):
        journal = JournalFactory(
            code='journal-1',
            localidentifier='journal-1',
        )
        IssueFactory(
            journal=journal,
            localidentifier='issue-1',
            year='2001',
            volume='1-2',
            number='3-4',
            publication_period='2001-2002',
        )
        IssueFactory(
            journal=journal,
            localidentifier='issue-2',
            year='2002',
            volume='3',
            number='1',
            publication_period='2001-2002',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', year=year, v=volume, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', year=year, v=volume, n=number)

    @pytest.mark.parametrize('volume, number, expected_url', [
        ('1', '2', '/fr/revues/journal-1/2001-v1-n2-issue-1/'),
        # If volume or number is omitted, the right issue should still be found.
        ('', '2', '/fr/revues/journal-1/2001-v1-n2-issue-1/'),
        ('1', '', '/fr/revues/journal-1/2001-v1-n2-issue-1/'),
    ])
    def test_get_redirect_url_with_volume_and_number(self, volume, number, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            volume='1',
            number='2',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', v=volume, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', v=volume, n=number)

    @pytest.mark.parametrize('year, volume, expected_url', [
        ('2001', '1', '/fr/revues/journal-1/2001-v1-issue-1/'),
        # If year or volume is omitted, the right issue should still be found.
        ('', '1', '/fr/revues/journal-1/2001-v1-issue-1/'),
        ('2001', '', '/fr/revues/journal-1/2001-v1-issue-1/'),
        # Wrong year or volume should raise 404.
        ('1999', '1', False),
        ('2001', '0', False),
    ])
    def test_get_redirect_url_with_year_and_volume(self, year, volume, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            volume='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', year=year, v=volume)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', year=year, v=volume)

    @pytest.mark.parametrize('volume, expected_url', [
        ('1', '/fr/revues/journal-1/2001-v1-issue-1/'),
        # Wrong volume should raise 404.
        ('0', False),
    ])
    def test_get_redirect_url_with_volume(self, volume, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            volume='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', v=volume)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', v=volume)

    @pytest.mark.parametrize('year, number, expected_url', [
        ('2001', '1', '/fr/revues/journal-1/2001-n1-issue-1/'),
        # If year or number is omitted, the right issue should still be found.
        ('', '1', '/fr/revues/journal-1/2001-n1-issue-1/'),
        ('2001', '', '/fr/revues/journal-1/2001-n1-issue-1/'),
        # Wrong year or number should raise 404.
        ('1999', '1', False),
        ('2001', '0', False),
    ])
    def test_get_redirect_url_with_year_and_number(self, year, number, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            number='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', year=year, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', year=year, n=number)

    @pytest.mark.parametrize('number, expected_url', [
        ('1', '/fr/revues/journal-1/2001-n1-issue-1/'),
        # Wrong number should raise 404.
        ('0', False),
    ])
    def test_get_redirect_url_with_number(self, number, expected_url):
        IssueFactory(
            journal__code='journal-1',
            localidentifier='issue-1',
            year='2001',
            number='1',
        )
        view = IssueDetailRedirectView()
        view.request = unittest.mock.MagicMock()
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal-1', n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal-1', n=number)
