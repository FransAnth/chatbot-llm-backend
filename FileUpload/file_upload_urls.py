from django.urls import path

from . import file_upload_views

urlpatterns = [path("upload/", file_upload_views.upload)]
