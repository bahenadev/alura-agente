import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from chat_page import chat_page
from docs_page import docs_page

for key, default in [
    ("historial", []),
    ("mensaje_documentos", ""),
    ("tipo_mensaje_documentos", "success"),
    ("mostrar_confirmacion_embeddings", False),
    ("upload_key", "uploader"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

st.sidebar.title("Asistente RAG")

pg = st.navigation(
    {
        "Navegación": [
            st.Page(chat_page, title="Chat", icon="💬"),
            st.Page(docs_page, title="Documentos", icon="📄"),
        ],
    },
    position="sidebar",
)
pg.run()
