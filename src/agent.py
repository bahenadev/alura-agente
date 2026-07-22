from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate

from retriever import buscar_contexto


CHAT_MODEL = "command-r7b-12-2024"


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
        return "No lo sé con la información disponible en los documentos."

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