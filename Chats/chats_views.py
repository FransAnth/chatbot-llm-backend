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
from .utils.chat_view_utils import ChatUtils
from .utils.open_ai_query import OpenAiQuery


class Chats(APIView):
    def __init__(self):
        self.chat_utils = ChatUtils()

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

        serializer = UserQuestionSerializer(data=chat_data)

        if serializer.is_valid():

            # Getting chat history and chat config
            chat_history = self.chat_utils.get_chat_history(
                user_id=chat_data["user_id"]
            )
            chat_config = ChatConfiguration.objects.get(user_id=chat_data["user_id"])

            # Chatbot query to get answers
            open_ai = OpenAiQuery(
                model_type=chat_config.model_type, instruction=chat_config.instruction
            )
            answer = open_ai.chat_retrieval(
                question=chat_data["question"], chat_history=chat_history
            )

            # open_ai = OpenAiQuery(
            #     model_type="deepseek-r1",
            #     instruction=chat_config.instruction,
            #     llm="ollama",
            # )
            # answer, think_content, processing_time = open_ai.chat(
            #     question=chat_data["question"], chat_history=chat_history
            # )

            # Saving the chat history
            self.chat_utils.save_chat_history(
                user_id=chat_data["user_id"],
                question=chat_data["question"],
                answer=answer,
            )

            return Response(
                {
                    "answer": answer,
                    "question": chat_data["question"],
                }
            )

            # return Response(
            #     {
            #         "answer": answer,
            #         "question": chat_data["question"],
            #         "observation": think_content,
            #         "processingTime": processing_time,
            #     }
            # )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_id = request.query_params.get("userId", None)

        if user_id is not None:
            try:
                chat_history_qs = ChatConversation.objects.filter(user_id=user_id)
                chat_history_qs.delete()

                return Response(
                    {"message": "Chat history has been Deleted."},
                    status=status.HTTP_200_OK,
                )

            except ChatConversation.DoesNotExist:
                return Response(
                    {
                        "message": f"Error deleting conversations for user-{user_id}. Chat history does not exist."
                    }
                )

            except Exception as error_message:
                return Response(
                    {
                        "message": "There was an error deleting the chat history",
                        "details": str(error_message),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"message": "No userId passed."}, status=status.HTTP_400_BAD_REQUEST
        )


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

                response_data = serializer.data
                response_data["message"] = "Chat configurations successfully updated!"

                return Response(response_data, status=status.HTTP_200_OK)

            error_response = serializer.errors
            error_response["message"] = "Opps, there has been an error saving your data"

            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        except ChatConfiguration.DoesNotExist:
            serializer = ChatConfigurationSerializer(data=config_data)

            if serializer.is_valid():
                serializer.save()

                response_data = serializer.data
                response_data["message"] = "Chat configurations successfully updated!"

                return Response(response_data, status=status.HTTP_200_OK)

            error_response = serializer.errors
            error_response["message"] = "Opps, there has been an error saving your data"

            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
