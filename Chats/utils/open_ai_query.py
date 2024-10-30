import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

from ..static.prompts import chat_prompt
from .chat_view_utils import ChatUtils

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class OpenAiQuery:
    def __init__(self, model_type="gpt-4o-mini", instruction=""):
        self.key = OPENAI_API_KEY
        self.model_type = model_type
        self.instruction = instruction
        self.chat_utils = ChatUtils()

    def chat(self, question, chat_history):

        template = self.chat_utils.get_template(
            prompt=chat_prompt, chat_history=chat_history, instruction=self.instruction
        )
        prompt = PromptTemplate(
            input_variables=["question"],
            template=template,
        )

        llm = ChatOpenAI(model=self.model_type, openai_api_key=self.key)
        chain = LLMChain(llm=llm, verbose=True, prompt=prompt)

        answer = chain.run(question)

        return answer
