import glob
import os

from chromadb import PersistentClient
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    DirectoryLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")


class VectorStore:
    def __init__(self):
        self.persist_directory = "storage/vectorstore/"
        self.CHROMA_SETTINGS = Settings(
            persist_directory=self.persist_directory,
            chroma_db_impl="duckdb+parquet",
            anonymized_telemetry=False,
        )
        self.collection_name = "vectorstore_db"

        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        client = PersistentClient(path=self.persist_directory)
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings,
            client=client,
        )

    # Creating Embeddings from local files
    def create_embeddings_from_local(self, path):

        doc_extension = path.split(".")[-1]

        match doc_extension:
            case "txt":
                loader = TextLoader(path)
            case "pdf":
                loader = PyPDFLoader(path)
            case "md":
                loader = UnstructuredMarkdownLoader(path)
            case "csv":
                loader = CSVLoader(path)
            case "docx":
                loader = Docx2txtLoader(path)
            case _:
                return False

        docs = loader.load()

        # splitting the text into
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        texts = text_splitter.split_documents(docs)

        ## here we are using OpenAI embeddings but in future we will swap out to local embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        vectordb = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory=self.persist_directory,  # Where to save data locally, remove if not necessary
        )

        print("TEXTS", texts)
        print("DOCS", docs)
        print("PATH", path)
        vectordb.add_documents(texts)

        return True
