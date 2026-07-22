import streamlit as st
from agent import responder_pregunta

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

st.title("Agente RAG")
st.write("Haz una pregunta sobre los documentos internos.")

pregunta = st.text_input("Escribe tu pregunta")

if st.button("Preguntar"):
    if pregunta.strip():
        with st.spinner("Buscando respuesta..."):
            respuesta = responder_pregunta(pregunta)
        st.subheader("Respuesta")
        st.write(respuesta)
    else:
        st.warning("Escribe una pregunta primero.")