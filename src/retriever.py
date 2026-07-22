from pathlib import Path

from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "rag_documents"

EMBEDDING_MODEL = "embed-v4.0"
TOP_K = 3


def buscar_contexto(pregunta: str, k: int = TOP_K):
    embeddings = CohereEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )

    resultados = vectorstore.similarity_search(pregunta, k=k)
    return resultados
