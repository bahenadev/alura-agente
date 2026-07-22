from pathlib import Path

DOCS_DIR = Path("docs")


def asegurar_directorio_docs():
    DOCS_DIR.mkdir(exist_ok=True)
    return DOCS_DIR


def guardar_archivos_subidos(uploaded_files):
    asegurar_directorio_docs()

    archivos_guardados = []

    for archivo in uploaded_files:
        ruta_destino = DOCS_DIR / archivo.name

        with open(ruta_destino, "wb") as f:
            f.write(archivo.getbuffer())

        archivos_guardados.append(archivo.name)

    return archivos_guardados


def listar_archivos_pdf():
    asegurar_directorio_docs()
    return sorted(DOCS_DIR.glob("*.pdf"))


def eliminar_archivo_pdf(nombre_archivo):
    asegurar_directorio_docs()
    ruta_archivo = DOCS_DIR / nombre_archivo

    if ruta_archivo.exists() and ruta_archivo.is_file():
        ruta_archivo.unlink()
        return True

    return False