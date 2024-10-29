from django.urls import path

from .views import file_upload_views

urlpatterns = [path("upload/", file_upload_views.upload)]
