import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chatbot_rag.utils.data_structure_utils import DataStructureUtils

from .models import ChatConfiguration, ChatConversation
from .serializers import (
    ChatConfigurationSerializer,
    ChatSerializer,
    UserQuestionSerializer,
)
from .utils.open_ai_query import OpenAiQuery


class Chats(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get("userId", None)
            chat_history_qs = ChatConversation.objects.all()

            if user_id is not None:
                chat_history_qs = chat_history_qs.filter(user_id=user_id)

            serializer = ChatSerializer(chat_history_qs, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as error_message:
            return Response(
                {"message": str(error_message)}, status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):

        data_util = DataStructureUtils()
        chat_data = data_util.json_to_dict(json.loads(request.body))

        print(f"CHAT DATAAA {chat_data}")

        serializer = UserQuestionSerializer(data=chat_data)

        if serializer.is_valid():
            chat_history = ChatConversation.objects.filter(
                user_id=chat_data["user_id"]
            ).order_by("timestamp")

            open_ai = OpenAiQuery()
            answer = open_ai.chat(
                question=chat_data["question"], chat_history=chat_history
            )

            return Response({"answer": answer, "question": chat_data["question"]})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatConfig(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get("userId", None)
            chat_config_qs = ChatConfiguration.objects.all()

            if user_id is not None:
                chat_config_qs = chat_config_qs.filter(user_id=user_id)

            serializer = ChatConfigurationSerializer(chat_config_qs, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as error_message:
            return Response(
                {"message", error_message}, status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        data_util = DataStructureUtils()
        request_data = json.loads(request.body)
        config_data = data_util.json_to_dict(request_data)

        user_id = request_data.get("userId")

        try:
            # Checking if config exists
            user = ChatConfiguration.objects.get(user_id=user_id)

            serializer = ChatConfigurationSerializer(
                user, data=config_data, partial=True
            )

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ChatConfiguration.DoesNotExist:
            serializer = ChatConfigurationSerializer(data=config_data)

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
