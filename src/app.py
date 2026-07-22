import streamlit as st
from agent import responder_pregunta

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

if "historial" not in st.session_state:
    st.session_state.historial = []


def limpiar_historial():
    st.session_state.historial = []


st.title("Agente RAG")

with st.sidebar:
    st.subheader("Controles")
    st.button("Limpiar conversación", on_click=limpiar_historial)

tab1, tab2 = st.tabs(["Chat", "Documentos"])

with tab1:
    st.write("Haz una pregunta sobre los documentos internos.")

    chat_container = st.container()

    with chat_container:
        for mensaje in st.session_state.historial:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

    pregunta = st.chat_input("Escribe tu pregunta")

    if pregunta:
        st.session_state.historial.append({"role": "user", "content": pregunta})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(pregunta)

            with st.chat_message("assistant"):
                with st.spinner("Buscando respuesta..."):
                    respuesta = responder_pregunta(pregunta)
                st.markdown(respuesta)

        st.session_state.historial.append({"role": "assistant", "content": respuesta})

with tab2:
    st.write("Aquí podrás gestionar tus archivos.")