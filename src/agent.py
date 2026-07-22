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
                    "Tu única fuente de información es el contexto proporcionado abajo.\n\n"
                    "Reglas estrictas:\n"
                    "- Si la pregunta del usuario no está relacionada con los documentos "
                    "(por ejemplo saludos, conversación casual, preguntas personales), "
                    "responde exactamente: 'No lo sé con la información disponible en los documentos.'\n"
                    "- Si el contexto no contiene la respuesta a la pregunta, "
                    "responde exactamente: 'No lo sé con la información disponible en los documentos.'\n"
                    "- No inventes información ni uses conocimiento externo.\n"
                    "- Siempre responde en español.\n"
                    "- Al final agrega una sección llamada 'Fuentes' listando los archivos "
                    "de los que obtuviste la información."
                ),
            ),
            (
                "human",
                (
                    "Pregunta del usuario:\n{pregunta}\n\n"
                    "Contexto recuperado:\n{contexto}\n\n"
                    "Instrucciones:\n"
                    "- Si el contexto está vacío o la pregunta no es sobre los documentos, "
                    "responde únicamente 'No lo sé con la información disponible en los documentos.'\n"
                    "- Si la respuesta está en el contexto, responde citando las fuentes."
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