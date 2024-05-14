import os

from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class OpenAiQuery:
    def __init__(self):
        self.key = OPENAI_API_KEY

    def chat(self, question, chat_history):

        prompt = PromptTemplate(
            input_variables=["question"],
            template="Answer the user question in a friendly way : Question {question}",
        )

        openai_model_name = "gpt-3.5-turbo-0613"
        llm = ChatOpenAI(model=openai_model_name, openai_api_key=self.key)
        chain = LLMChain(llm=llm, verbose=True, prompt=prompt)

        answer = chain.run(question)

        return answer
