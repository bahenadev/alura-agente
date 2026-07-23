import re

from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate

from retriever import buscar_contexto
from build_index import obtener_metadata_documentos


CHAT_MODEL = "command-r7b-12-2024"

PATRON_SALUDO = re.compile(
    r"^(hola|buenos\s+d[ií]as|buenas\s+tardes|buenas\s+noches|buen[a]?\s+d[ií]a|buena\s+tarde|buena\s+noche|qu[eé]\s+tal|saludos|hey|buenas)([\s\?,!;.:]*.*)?$",
    re.IGNORECASE,
)

PATRON_META = re.compile(
    r"(qué\s+(puedes|sabes|sabes\s+hacer|info|informaci[oó]n|tienes)|"
    r"de\s+qu[eé]\s+(son|tratan|tratan?\s+los\s+documentos)|"
    r"qu[eé]\s+documentos?\s+(hay|tienes|ten[eé]s)|"
    r"(cu[aá]les|cu[aá]ntos?)\s+(son|documentos?|archivos?)|"
    r"(lista|enumera|muestra|mu[eé]strame|dime)\s+(los\s+)?(documentos|archivos|temas)|"
    r"sobre\s+qu[eé]\s+(puedes|contestas|respondes|hablas))",
    re.IGNORECASE,
)


def _es_saludo(texto: str) -> bool:
    return bool(PATRON_SALUDO.match(texto.strip()))


def _es_pregunta_meta(texto: str) -> bool:
    return bool(PATRON_META.search(texto.strip()))


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

    if _es_pregunta_meta(pregunta):
        metadata = obtener_metadata_documentos()
        return metadata

    documentos = buscar_contexto(pregunta)

    metadata = obtener_metadata_documentos()

    if documentos:
        contexto = formatear_contexto(documentos)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Eres un asistente RAG para documentos internos de una empresa. "
                        "Responde únicamente con base en el contexto proporcionado.\n\n"
                        "Documentos disponibles:\n{metadata}\n\n"
                        "Reglas:\n"
                        "- Si el contexto contiene la respuesta, responde de forma clara y breve.\n"
                        "- Si el contexto no contiene la respuesta, indica que esa información "
                        "no está en los documentos y sugiere qué temas sí puedes cubrir.\n"
                        "- No inventes información ni uses conocimiento externo.\n"
                        "- Siempre responde en español.\n"
                        "- Al final agrega una sección llamada 'Fuentes' listando los archivos "
                        "de los que obtuviste la información."
                    ),
                ),
                (
                    "human",
                    "Pregunta: {pregunta}\n\nContexto:\n{contexto}",
                ),
            ]
        )

        llm = ChatCohere(model=CHAT_MODEL, temperature=0)
        chain = prompt | llm
        respuesta = chain.invoke(
            {
                "pregunta": pregunta,
                "contexto": contexto,
                "metadata": metadata,
            }
        )

        return respuesta.content

    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Eres un asistente RAG para documentos internos de una empresa. "
                        "No encontraste fragmentos relevantes en los documentos para esta pregunta.\n\n"
                        "Documentos disponibles:\n{metadata}\n\n"
                        "Reglas:\n"
                        "- Si la pregunta es sobre un tema que podría estar en los documentos, "
                        "indica que no encontraste información específica y sugiere reformular.\n"
                        "- Si la pregunta es ajena a los documentos, responde: "
                        "'Solo respondo preguntas sobre los documentos indexados.' "
                        "y muestra los temas disponibles.\n"
                        "- No inventes información.\n"
                        "- Siempre responde en español."
                    ),
                ),
                (
                    "human",
                    "Pregunta: {pregunta}",
                ),
            ]
        )

        llm = ChatCohere(model=CHAT_MODEL, temperature=0)
        chain = prompt | llm
        respuesta = chain.invoke(
            {
                "pregunta": pregunta,
                "metadata": metadata,
            }
        )

        return respuesta.content
