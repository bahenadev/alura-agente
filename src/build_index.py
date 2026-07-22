import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_core.documents import Document

from load_documents import load_all_documents, chunk_documents

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "documentos_empresa"


def build_index():
    if not COHERE_API_KEY:
        raise ValueError("No se encontró COHERE_API_KEY en el archivo .env")

    documents = load_all_documents()

    if not documents:
        raise ValueError("No se encontraron documentos válidos en la carpeta docs/")

    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError("No se pudieron generar chunks a partir de los documentos")

    langchain_docs = [
        Document(
            page_content=chunk["content"],
            metadata=chunk["metadata"]
        )
        for chunk in chunks
    ]

    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY,
        model="embed-multilingual-v3.0"
    )

    Chroma.from_documents(
        documents=langchain_docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME
    )


if __name__ == "__main__":
    build_index()