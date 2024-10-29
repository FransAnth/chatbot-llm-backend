from rest_framework import serializers

from .models import ChatConfiguration, ChatConversation


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatConversation
        fields = "__all__"


class UserQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatConversation
        fields = ["user_id", "question"]


class ChatConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatConfiguration
        fields = "__all__"
