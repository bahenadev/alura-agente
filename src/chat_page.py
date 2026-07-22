import streamlit as st

from agent import responder_pregunta


def limpiar_historial():
    st.session_state.historial = []


def chat_page():
    col_titulo, col_boton = st.columns([5, 1], vertical_alignment="center")

    with col_titulo:
        st.title("Asistente RAG")

    with col_boton:
        st.button(
            "Limpiar",
            on_click=limpiar_historial,
            use_container_width=True,
        )

    st.markdown(
        """
        <style>
        .st-key-chat_messages {
            height: calc(100dvh - 200px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="chat_messages", height=500):
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

    pregunta = st.chat_input("Escribe tu pregunta")

    if pregunta:
        st.session_state.pending_question = pregunta
        st.rerun()
