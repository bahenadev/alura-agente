import streamlit as st
from agent import responder_pregunta

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

st.title("Agente RAG")
st.write("Haz una pregunta sobre los documentos internos.")

if "historial" not in st.session_state:
    st.session_state.historial = []


def limpiar_historial():
    st.session_state.historial = []


with st.sidebar:
    st.subheader("Controles")
    st.button("Limpiar conversación", on_click=limpiar_historial)

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

pregunta = st.chat_input("Escribe tu pregunta")

if pregunta:
    st.session_state.historial.append({"role": "user", "content": pregunta})

    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando respuesta..."):
            respuesta = responder_pregunta(pregunta)
        st.markdown(respuesta)

    st.session_state.historial.append({"role": "assistant", "content": respuesta})