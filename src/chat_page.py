import streamlit as st

from agent import responder_pregunta


def limpiar_historial():
    st.session_state.historial = []


def chat_page():
    st.title("Asistente RAG")

    col_texto, col_boton = st.columns([5, 1], vertical_alignment="bottom")

    with col_texto:
        st.write("Haz una pregunta sobre los documentos internos.")

    with col_boton:
        st.button(
            "Limpiar",
            on_click=limpiar_historial,
            use_container_width=True,
        )

    historial_box = st.container(height=500, border=True)

    with historial_box:
        for mensaje in st.session_state.historial:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

        if "pending_question" in st.session_state:
            pregunta_pendiente = st.session_state.pop("pending_question")

            with st.chat_message("user"):
                st.markdown(pregunta_pendiente)

            with st.chat_message("assistant"):
                with st.spinner("Buscando respuesta...", show_time=True):
                    try:
                        respuesta = responder_pregunta(pregunta_pendiente)
                    except Exception as e:
                        respuesta = f"Ocurrió un error al generar la respuesta: {e}"

                st.markdown(respuesta)

            st.session_state.historial.append(
                {"role": "user", "content": pregunta_pendiente}
            )
            st.session_state.historial.append(
                {"role": "assistant", "content": respuesta}
            )

            st.rerun()

    prompt = st.bottom.chat_input("Escribe tu pregunta")

    if prompt:
        st.session_state.pending_question = prompt
        st.rerun()
