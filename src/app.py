import streamlit as st
from agent import responder_pregunta

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

st.title("Agente RAG")
st.write("Haz una pregunta sobre los documentos internos.")

if "historial" not in st.session_state:
    st.session_state.historial = []

pregunta = st.text_input("Escribe tu pregunta")

if st.button("Preguntar"):
    if pregunta.strip():
        with st.spinner("Buscando respuesta..."):
            respuesta = responder_pregunta(pregunta)

        st.session_state.historial.append({
            "pregunta": pregunta,
            "respuesta": respuesta
        })
    else:
        st.warning("Escribe una pregunta primero.")

if st.session_state.historial:
    st.subheader("Historial de conversación")

    for item in reversed(st.session_state.historial):
        st.markdown(f"**Tú:** {item['pregunta']}")
        st.markdown(f"**Agente:** {item['respuesta']}")
        st.divider()