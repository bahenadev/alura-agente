import streamlit as st
from agent import responder_pregunta
from file_manager import guardar_archivos_subidos, listar_archivos_pdf

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

if "historial" not in st.session_state:
    st.session_state.historial = []


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
        archivos_guardados = guardar_archivos_subidos(uploaded_files)

        if archivos_guardados:
            st.success("Archivos guardados correctamente:")
            for nombre in archivos_guardados:
                st.markdown(f"- {nombre}")

    archivos_en_disco = listar_archivos_pdf()

    st.subheader("Archivos disponibles")
    if archivos_en_disco:
        for archivo in archivos_en_disco:
            st.markdown(f"- {archivo.name}")
    else:
        st.info("No hay archivos guardados en la carpeta docs.")