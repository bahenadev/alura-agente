import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_cohere import ChatCohere
from retriever import buscar_contexto

load_dotenv()

PROMPT_SISTEMA = """
Eres un asistente para responder preguntas sobre documentos internos de una empresa.

Debes seguir estas reglas estrictamente:
1. Responde únicamente con información que aparezca en el contexto proporcionado.
2. No inventes datos ni completes información con conocimiento externo.
3. Si la respuesta no está en el contexto, responde exactamente:
No lo sé con la información disponible.
4. Al final de tu respuesta agrega una línea con este formato:
Fuente: <nombre_del_archivo>
5. Sé claro, breve y directo.
""".strip()


def formatear_contexto(documentos):
    bloques = []

    for i, doc in enumerate(documentos, start=1):
        fuente = doc.metadata.get("source", "Sin fuente")
        chunk_id = doc.metadata.get("chunk_id", "Sin chunk_id")
        contenido = doc.page_content.strip()

        bloque = f"""
Fragmento {i}
Fuente: {fuente}
Chunk ID: {chunk_id}
Contenido:
{contenido}
""".strip()

        bloques.append(bloque)

    return "\n\n---\n\n".join(bloques)


def responder_pregunta(pregunta: str):
    documentos = buscar_contexto(pregunta, k=3)
    contexto = formatear_contexto(documentos)

    llm = ChatCohere(
    model="command-r-plus-08-2024",
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    temperature=0
    )

    mensajes = [
        SystemMessage(content=PROMPT_SISTEMA),
        HumanMessage(
            content=f"""
Contexto:
{contexto}

Pregunta:
{pregunta}
""".strip()
        )
    ]

    respuesta = llm.invoke(mensajes)
    return respuesta.content


if __name__ == "__main__":
    pregunta = "¿Qué tecnologías usa el Chapter de Back-end?"
    respuesta = responder_pregunta(pregunta)

    print("\nRespuesta:\n")
    print(respuesta)