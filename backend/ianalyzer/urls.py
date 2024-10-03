"""ianalyzer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from addcorpus import urls as corpus_urls
from addcorpus.views import (CorpusDataFileViewSet, CorpusDefinitionViewset,
                             CorpusDocumentationPageViewset)
from api import urls as api_urls
from api.views import QueryViewset
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from download import urls as download_urls
from es import urls as es_urls
from media import urls as media_urls
from rest_framework import routers
from tag import urls as tag_urls
from tag.views import TagViewSet
from visualization import urls as visualization_urls
from wordmodels import urls as wordmodels_urls

from .index import index
from .proxy_frontend import proxy_frontend

api_router = routers.DefaultRouter()  # register viewsets with this router
api_router.register('search_history', QueryViewset, basename='query')
api_router.register('tag/tags', TagViewSet)
api_router.register('corpus/definitions', CorpusDefinitionViewset, basename='corpus')
api_router.register('corpus/datafiles',
                    CorpusDataFileViewSet, basename='datafiles')
api_router.register('corpus/documentation', CorpusDocumentationPageViewset, basename='corpus-documentation')

if settings.PROXY_FRONTEND:
    spa_url = re_path(r'^(?P<path>.*)$', proxy_frontend)
else:
    spa_url = re_path(r'', index)

urlpatterns = [
    path('admin', RedirectView.as_view(url='/admin/', permanent=True)),
    path('api', RedirectView.as_view(url='/api/', permanent=True)),
    path('api-auth', RedirectView.as_view(url='/api-auth/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/', include(api_router.urls)),
    path('api/', include(api_urls)),
    path('api/', include(media_urls)),
    path('api/corpus/', include(corpus_urls)),
    path('api/visualization/', include(visualization_urls)),
    path('api/download/', include(download_urls)),
    path('api/wordmodels/', include(wordmodels_urls)),
    path('api/es/', include(es_urls)),
    path('api/tag/', include(tag_urls)),
    path('api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework',
    )),
    path('users/', include('users.urls')),
    spa_url,  # catch-all; unknown paths to be handled by a SPA
]
