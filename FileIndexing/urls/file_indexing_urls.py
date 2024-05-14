from django.urls import path

from ..views import file_indexing_views

urlpatterns = [path("", file_indexing_views.file_indexing)]
