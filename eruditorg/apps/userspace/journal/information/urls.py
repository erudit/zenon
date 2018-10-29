# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(_(r'^$'),
        views.JournalInformationUpdateView.as_view(), name='update'),
    url(_(r'^supprimer_collaborateur$'),
        views.JournalInformationCollaboratorDeleteView.as_view(), name='delete_contributor'),
]
