import streamlit as st
from agent import responder_pregunta

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

if "historial" not in st.session_state:
    st.session_state.historial = []

if "documentos_cargados" not in st.session_state:
    st.session_state.documentos_cargados = []


def limpiar_historial():
    st.session_state.historial = []


st.title("Agente RAG")

tab1, tab2 = st.tabs(["Chat", "Documentos"])

with tab1:
    col_texto, col_boton = st.columns([5, 1], vertical_alignment="bottom")

    with col_texto:
        st.write("Haz una pregunta sobre los documentos internos.")

    with col_boton:
        st.button("Limpiar", on_click=limpiar_historial, use_container_width=True)

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
    st.write("Aquí podrás gestionar tus archivos PDF.")

    uploaded_files = st.file_uploader(
        "Sube uno o varios archivos PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        nombres_actuales = [archivo.name for archivo in uploaded_files]
        st.session_state.documentos_cargados = nombres_actuales

    if st.session_state.documentos_cargados:
        st.subheader("Archivos cargados")
        for nombre in st.session_state.documentos_cargados:
            st.markdown(f"- {nombre}")
    else:
        st.info("Aún no has cargado documentos.")