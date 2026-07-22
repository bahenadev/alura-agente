from pathlib import Path

from langchain_chroma import Chroma
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_core.prompts import ChatPromptTemplate


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "rag_documents"

EMBEDDING_MODEL = "embed-v4.0"
CHAT_MODEL = "command-r7b-12-2024"
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


def formatear_contexto(documentos) -> str:
    bloques = []

    for i, doc in enumerate(documentos, start=1):
        fuente = doc.metadata.get("source_file", "Fuente desconocida")
        pagina = doc.metadata.get("page", "N/D")
        contenido = doc.page_content.strip()

        bloque = (
            f"[Fragmento {i}]\n"
            f"Fuente: {fuente}\n"
            f"Página: {pagina}\n"
            f"Contenido:\n{contenido}"
        )
        bloques.append(bloque)

    return "\n\n".join(bloques)


def responder_pregunta(pregunta: str) -> str:
    documentos = buscar_contexto(pregunta)

    if not documentos:
        return "No encontré contexto suficiente en la base documental."

    contexto = formatear_contexto(documentos)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Eres un asistente RAG para documentos internos de una empresa. "
                    "Responde únicamente con base en el contexto recuperado. "
                    "Si la respuesta no está claramente en el contexto, di: "
                    "'No lo sé con la información disponible en los documentos.' "
                    "Responde en español y al final agrega una sección breve llamada "
                    "'Fuentes' listando los archivos utilizados."
                ),
            ),
            (
                "human",
                (
                    "Pregunta del usuario:\n{pregunta}\n\n"
                    "Contexto recuperado:\n{contexto}\n\n"
                    "Instrucciones:\n"
                    "- No inventes información.\n"
                    "- Da una respuesta clara y breve.\n"
                    "- Si aplica, menciona pasos o requisitos exactos.\n"
                    "- Cierra con la sección 'Fuentes'."
                ),
            ),
        ]
    )

    llm = ChatCohere(model=CHAT_MODEL, temperature=0)

    chain = prompt | llm
    respuesta = chain.invoke(
        {
            "pregunta": pregunta,
            "contexto": contexto,
        }
    )

    return respuesta.content