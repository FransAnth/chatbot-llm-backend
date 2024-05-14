from django.urls import path

from ..views import chats_views

urlpatterns = [path("chats/", chats_views.chats)]
