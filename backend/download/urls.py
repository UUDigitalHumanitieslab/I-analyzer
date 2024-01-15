from django.urls import path
from download.views import *

urlpatterns = [
    path('search_results', ResultsDownloadView.as_view()),
    path('search_results_task', ResultsDownloadTaskView.as_view()),
    path('full_data', FullDataDownloadTaskView.as_view()),
    path('csv/<str:id>', FileDownloadView.as_view(), name='download-csv')
]
