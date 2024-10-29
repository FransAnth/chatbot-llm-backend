import glob
import os

import boto3
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

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

    def create_embedding(self):
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        if self.does_vectorstore_exist(self.persist_directory):
            pass

        else:
            texts = self.process_documents()
            print(f"Creating embeddings. May take some minutes...")
            db = Chroma.from_documents(
                texts,
                embeddings,
                persist_directory=self.persist_directory,
                client_settings=self.CHROMA_SETTINGS,
                collection_name=self.collection_name,
            )
            db.persist()
            db = None

    def process_documents(self, org_id, existing_file_paths):
        """
        Load documents and split in chunks
        """

        documents = self.load_documents(org_id, existing_file_paths)
        if not documents:
            print("No new documents to load")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        texts = text_splitter.split_documents(documents)
        print(
            f"Split into {len(texts)} chunks of text (max. {self.chunk_size} tokens each)"
        )
        return texts

    def load_documents(self, org_id, existing_file_paths):
        """
        Loads all documents from the source documents directory, ignoring specified files
        """

        filtered_files = self.bucket.objects.filter(Prefix=str(org_id) + "/")
        count_obj = 0
        results = []
        s3 = boto3.client("s3")
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=self.bucket_name, Prefix=str(org_id) + "/"
        ):
            # Pull out each list of objects from each page
            for cur in page.get("Contents", []):
                # Check each object to see if it matches the target criteria
                if cur["LastModified"] >= self.dt_last_success_run:
                    # If so, add it to the final list
                    if not cur["Key"].endswith("/"):
                        key_already_exists = cur["Key"] in existing_file_paths
                        print(f"Key: {cur['Key']} exists? {key_already_exists}")
                        if not key_already_exists:
                            response = s3.get_object_tagging(
                                Bucket=self.bucket.name, Key=cur["Key"]
                            )
                            if response["TagSet"] is not None:
                                cur["TagSet"] = response["TagSet"]

                            results.extend(self.load_single_s3_document(cur))

        return results

    def does_vectorstore_exist(self, persist_directory: str):
        """
        Checks if vectorstore exists
        """
        if os.path.exists(os.path.join(persist_directory, "index")):
            if os.path.exists(
                os.path.join(persist_directory, "chroma-collections.parquet")
            ) and os.path.exists(
                os.path.join(persist_directory, "chroma-embeddings.parquet")
            ):
                list_index_files = glob.glob(
                    os.path.join(persist_directory, "index/*.bin")
                )
                list_index_files += glob.glob(
                    os.path.join(persist_directory, "index/*.pkl")
                )
                # At least 3 documents are needed in a working vectorstore
                if len(list_index_files) > 3:
                    return True
        return False

    # Creating Embeddings from local files
    def create_embeddings_from_local(self, path):

        # Load and process the text files
        loader = DirectoryLoader(path=path, glob="**/*.md", use_multithreading=True)
        docs = loader.load()

        # splitting the text into
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        texts = text_splitter.split_documents(docs)

        ## here we are using OpenAI embeddings but in future we will swap out to local embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        vectordb = Chroma.from_documents(
            texts,
            embeddings,
            persist_directory=self.persist_directory,
            client_settings=self.CHROMA_SETTINGS,
            # collection_name=self.collection_name,
        )
        vectordb.persist()
        vectordb = None

        # persiste the db to disk
        vectordb.persist()
        vectordb = None
