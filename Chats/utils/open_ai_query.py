import os
import re
import time

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ..static.prompts import chat_prompt, chat_retrieval_prompt
from .chat_view_utils import ChatUtils

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class OpenAiQuery:
    def __init__(self, model_type="gpt-4o-mini", instruction="", llm="open_ai"):
        self.key = OPENAI_API_KEY
        self.model_type = model_type
        self.instruction = instruction
        self.chat_utils = ChatUtils()
        self.collection_name = "vectorstore_db"
        self.persist_directory = "storage/vectorstore/"

        if llm == "open_ai":
            self.llm = ChatOpenAI(model=self.model_type, openai_api_key=self.key)
        elif llm == "ollama":
            self.llm = OllamaLLM(model=model_type)
        else:
            self.llm = ChatOpenAI(model=self.model_type, openai_api_key=self.key)

    def chat(self, question, chat_history=[]):
        template = self.chat_utils.get_template(
            prompt=chat_prompt,
            chat_history=chat_history,
            instruction=self.instruction,
        )
        prompt = template.replace("{question}", question)

        start_time = time.time()
        response = self.llm.invoke(prompt)
        end_time = time.time()
        processing_time = round(end_time - start_time, 4)

        try:
            think_content = None
            answer = response.content
        except:
            # Extract the content inside <think> tags
            think_match = re.search(r"<think>(.*?)</think>", response, re.DOTALL)
            think_content = think_match.group(1).strip()
            response = re.sub(
                r"<think>.*?</think>", "", response, flags=re.DOTALL
            ).strip()

            answer = response

        return (answer, think_content, processing_time)

    def chat_retrieval(self, question, chat_history=[]):

        template = self.chat_utils.get_template(
            prompt=chat_retrieval_prompt,
            chat_history=chat_history,
            instruction=self.instruction,
        )
        prompt = PromptTemplate(
            input_variables=["question"], template=template, template_format="jinja2"
        )

        embeddings = OpenAIEmbeddings(openai_api_key=self.key)

        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory=self.persist_directory,  # Where to save data locally, remove if not necessary
        )

        chain = RetrievalQA.from_chain_type(
            chain_type_kwargs={"verbose": True, "prompt": prompt},
            retriever=vectorstore.as_retriever(),
            chain_type="stuff",
            return_source_documents=True,
            llm=self.llm,
        )

        res = chain.invoke(question)

        answer = res["result"]
        docs = res["source_documents"]

        return answer
