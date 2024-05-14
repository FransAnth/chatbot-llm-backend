from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import ChatConversation
from ..utils.open_ai_query import OpenAiQuery


@api_view(["POST", "GET"])
def chats(request):

    match (request.method):
        case "GET":
            chat_history = ChatConversation().objects.get(pk=id)

            data = list(chat_history.values())

            return Response({"data": data})

        case "POST":
            data = request.data.copy()
            question = data.get("question")
            chat_history = data.get("chat_history", [])

            open_ai = OpenAiQuery()
            answer = open_ai.chat(question=question, chat_history=chat_history)

            return Response({"answer": answer, "question": question})
