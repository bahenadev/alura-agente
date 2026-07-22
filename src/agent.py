import re

from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate

from retriever import buscar_contexto


CHAT_MODEL = "command-r7b-12-2024"

PATRON_SALUDO = re.compile(
    r"^(hola|buenos\s+d[ií]as|buenas\s+tardes|buenas\s+noches|buen[a]?\s+d[ií]a|buena\s+tarde|buena\s+noche|qu[eé]\s+tal|saludos|hey|buenas)([\s\?,!;.:]*.*)?$",
    re.IGNORECASE,
)


def _es_saludo(texto: str) -> bool:
    return bool(PATRON_SALUDO.match(texto.strip()))


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
    if _es_saludo(pregunta):
        return "¡Hola! Soy tu asistente de documentos internos. Hazme una pregunta sobre los documentos y con gusto te ayudaré."

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
                    "Responde únicamente con base en el contexto proporcionado.\n\n"
                    "Reglas:\n"
                    "- Si el contexto contiene la respuesta, responde de forma clara y breve.\n"
                    "- Si el contexto no contiene la respuesta, "
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
                    "Pregunta: {pregunta}\n\n"
                    "Contexto:\n{contexto}"
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