import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import responder_pregunta
from build_index import (
    build_index,
    hay_cambios_pendientes,
    obtener_resumen_indexacion,
)
from file_manager import (
    guardar_archivos_subidos,
    listar_archivos_pdf,
    eliminar_archivo_pdf,
)

st.set_page_config(page_title="Agente RAG", page_icon="🤖", layout="centered")

if "historial" not in st.session_state:
    st.session_state.historial = []

if "mensaje_documentos" not in st.session_state:
    st.session_state.mensaje_documentos = ""

if "tipo_mensaje_documentos" not in st.session_state:
    st.session_state.tipo_mensaje_documentos = "success"

if "mostrar_confirmacion_embeddings" not in st.session_state:
    st.session_state.mostrar_confirmacion_embeddings = False


def limpiar_historial():
    st.session_state.historial = []


def mostrar_confirmacion_embeddings():
    st.session_state.mostrar_confirmacion_embeddings = True


def cancelar_confirmacion_embeddings():
    st.session_state.mostrar_confirmacion_embeddings = False
    st.session_state.mensaje_documentos = "La preparación de embeddings fue cancelada."
    st.session_state.tipo_mensaje_documentos = "info"


st.title("Agente RAG")

tab1, tab2 = st.tabs(["Chat", "Documentos"])

with tab1:
    col_texto, col_boton = st.columns([5, 1], vertical_alignment="bottom")

    with col_texto:
        st.write("Haz una pregunta sobre los documentos internos.")

    with col_boton:
        st.button("Limpiar", on_click=limpiar_historial, use_container_width=True)

    for mensaje in st.session_state.historial:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    pregunta = st.chat_input("Escribe tu pregunta")

    if pregunta:
        st.session_state.historial.append({"role": "user", "content": pregunta})

        with st.chat_message("user"):
            st.markdown(pregunta)

        with st.chat_message("assistant"):
            with st.spinner("Buscando respuesta...", show_time=True):
                try:
                    respuesta = responder_pregunta(pregunta)
                except Exception as e:
                    respuesta = f"Ocurrió un error al generar la respuesta: {e}"

            st.markdown(respuesta)

        st.session_state.historial.append({"role": "assistant", "content": respuesta})

with tab2:
    st.write("Aquí podrás gestionar tus archivos PDF.")

    uploaded_files = st.file_uploader(
        "Selecciona uno o varios archivos PDF",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        archivos_guardados = guardar_archivos_subidos(uploaded_files)

        if archivos_guardados:
            st.session_state.mensaje_documentos = "Archivos guardados correctamente."
            st.session_state.tipo_mensaje_documentos = "success"
            st.session_state.mostrar_confirmacion_embeddings = False

    if st.session_state.mensaje_documentos:
        if st.session_state.tipo_mensaje_documentos == "success":
            st.success(st.session_state.mensaje_documentos)
        elif st.session_state.tipo_mensaje_documentos == "error":
            st.error(st.session_state.mensaje_documentos)
        else:
            st.info(st.session_state.mensaje_documentos)

    archivos_en_disco = listar_archivos_pdf()

    st.subheader("Archivos disponibles")

    if archivos_en_disco:
        for archivo in archivos_en_disco:
            col_nombre, col_boton = st.columns([5, 1], vertical_alignment="center")

            with col_nombre:
                st.markdown(f"**{archivo.name}**")

            with col_boton:
                if st.button("Eliminar", key=f"eliminar_{archivo.name}"):
                    eliminado = eliminar_archivo_pdf(archivo.name)

                    if eliminado:
                        st.session_state.mensaje_documentos = f"Archivo eliminado: {archivo.name}"
                        st.session_state.tipo_mensaje_documentos = "success"
                    else:
                        st.session_state.mensaje_documentos = f"No se pudo eliminar: {archivo.name}"
                        st.session_state.tipo_mensaje_documentos = "error"

                    st.session_state.mostrar_confirmacion_embeddings = False
                    st.rerun()
    else:
        st.info("No hay archivos guardados en la carpeta docs.")

    st.divider()
    st.subheader("Embeddings")

    if archivos_en_disco:
        resumen = obtener_resumen_indexacion()
        cambios_pendientes = hay_cambios_pendientes()

        if resumen["inicializado"]:
            st.caption(
                f"Última indexación: {resumen['total_archivos_indexados']} archivo(s) registrados."
            )
        else:
            st.caption("Aún no existe una indexación previa.")

        if cambios_pendientes:
            if resumen["inicializado"]:
                st.warning(
                    "Se detectaron cambios en los documentos. "
                    "Puedes preparar embeddings para actualizar el índice.",
                    icon="⚠️"
                )
            else:
                st.warning(
                    "Aún no se ha generado el índice vectorial. "
                    "Prepara los embeddings para poder hacer preguntas.",
                    icon="⚠️"
                )
        else:
            st.info(
                "No hay cambios en los documentos desde la última indexación. "
                "Se bloquea la ejecución para evitar reprocesamiento innecesario."
            )

        st.button(
            "Preparar embeddings",
            on_click=mostrar_confirmacion_embeddings,
            disabled=not cambios_pendientes,
            use_container_width=True
        )

        if st.session_state.mostrar_confirmacion_embeddings and cambios_pendientes:
            if resumen["inicializado"]:
                st.warning(
                    "Esta acción actualizará el índice vectorial con los documentos actuales. "
                    "Se reemplazará el contenido anterior. Puede tardar varios segundos.",
                    icon="⚠️"
                )
            else:
                st.warning(
                    "Esta acción generará embeddings a partir de tus documentos PDF "
                    "y creará el índice vectorial. Puede tardar varios segundos.",
                    icon="⚠️"
                )

            col_confirmar, col_cancelar = st.columns(2)

            with col_confirmar:
                if st.button("Sí, continuar", use_container_width=True):
                    try:
                        with st.spinner("Generando embeddings e indexando documentos...", show_time=True):
                            resultado = build_index()

                        st.session_state.mensaje_documentos = (
                            "Embeddings generados correctamente. "
                            f"Archivos procesados: {resultado['archivos_procesados']}."
                        )
                        st.session_state.tipo_mensaje_documentos = "success"
                    except Exception as e:
                        st.session_state.mensaje_documentos = (
                            f"Ocurrió un error al generar embeddings: {e}"
                        )
                        st.session_state.tipo_mensaje_documentos = "error"

                    st.session_state.mostrar_confirmacion_embeddings = False
                    st.rerun()

            with col_cancelar:
                st.button(
                    "Cancelar",
                    on_click=cancelar_confirmacion_embeddings,
                    use_container_width=True
                )
    else:
        st.info("Sube al menos un PDF antes de preparar embeddings.")