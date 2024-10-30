from ..models import ChatConversation
from ..serializers import ChatSerializer


class ChatUtils:
    def save_chat_history(self, question, answer, user_id):
        chat_history_data = {
            "user_id": user_id,
            "question": question,
            "answer": answer,
        }
        serializer = ChatSerializer(data=chat_history_data, partial=True)

        if serializer.is_valid():
            serializer.save()

            print("Chat History Saved")
            return True

        raise ValueError(serializer.errors)

    def get_chat_history(self, user_id, limit=None):
        chat_hist_qs = ChatConversation.objects.filter(user_id=user_id).order_by(
            "timestamp"
        )
        chat_hist_serializer = ChatSerializer(chat_hist_qs, many=True)
        chat_history = chat_hist_serializer.data

        return chat_history

    def get_template(self, prompt, chat_history, instruction):
        prompt = prompt.replace("{instruction}", instruction)
        prompt = prompt.replace(
            "{chat_history}", self.contruct_chat_history(chat_history)
        )

        return prompt

    def contruct_chat_history(self, chat_history):
        chat_history_prompt = """"""

        print("CHAT HISTORY", chat_history)

        if len(chat_history) > 0:
            for chat in chat_history:
                question = (
                    chat["question"]
                    if len(chat["question"]) < 400
                    else chat["question"][0:400] + "..."
                )
                answer = (
                    chat["answer"]
                    if len(chat["answer"]) < 400
                    else chat["answer"][0:400] + "..."
                )

                history = f"""
                    User : {question}
                    Your Response :  {answer}
                """

                chat_history_prompt += history
        else:
            chat_history_prompt = "No chat history"

        return chat_history_prompt
