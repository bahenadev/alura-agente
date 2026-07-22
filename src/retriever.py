import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "documentos_empresa"


def buscar_contexto(pregunta: str, k: int = 3):
    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    embeddings = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY")
    )

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    resultados = vectorstore.similarity_search(pregunta, k=k)
    return resultados


if __name__ == "__main__":
    pregunta = "¿Cuál es la cobertura mínima de pruebas unitarias exigida para aprobar un Code Review?"
    resultados = buscar_contexto(pregunta)

    print(f"\nPregunta: {pregunta}\n")
    print(f"Se encontraron {len(resultados)} resultados.\n")

    for i, doc in enumerate(resultados, start=1):
        print(f"--- Resultado {i} ---")
        print(f"Fuente: {doc.metadata.get('source', 'Sin fuente')}")
        print(f"Chunk ID: {doc.metadata.get('chunk_id', 'Sin chunk_id')}")
        print(doc.page_content[:700])
        print()