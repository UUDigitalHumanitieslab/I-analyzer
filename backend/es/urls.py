from django.urls import path
from es.views import ForwardSearchView, NamedEntitySearchView

urlpatterns = [
    path('<str:corpus>/_search', ForwardSearchView.as_view()),
    path('<str:corpus>/<str:id>/named_entities',
         NamedEntitySearchView.as_view())
]
