from django.urls import path

from .views.chats_views import Chats

urlpatterns = [path("chats/", Chats.as_view())]
