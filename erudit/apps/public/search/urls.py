# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.Search.as_view(), name='search'),
    url(r'^v2/$', views.SearchResultsView.as_view(), name='results'),
    url(r'^api/eruditdocuments/', views.EruditDocumentListAPIView.as_view(),
        name='eruditdocument-api-list'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
