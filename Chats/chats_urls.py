from django.urls import path

from .chats_views import ChatConfig, Chats

urlpatterns = [
    path("chats/", Chats.as_view()),
    path("chats/config/", ChatConfig.as_view()),
]
