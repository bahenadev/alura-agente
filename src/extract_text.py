import os
from pypdf import PdfReader

# Obtener la ruta absoluta de la carpeta donde está este archivo (src/)
# __file__ representa el archivo actual: extract_text.py
# os.path.abspath(__file__) convierte esa ruta en una ruta completa
# os.path.dirname(...) se queda solo con la carpeta contenedora
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta hacia la carpeta docs/
# BASE_DIR apunta a src/, entonces con ".." subimos un nivel
# y luego entramos a la carpeta docs
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")

# Listar todo lo que existe dentro de la carpeta docs/
# os.listdir devuelve una lista de nombres de archivos y carpetas
archivos = os.listdir(DOCS_DIR)

# Crear una lista vacía para guardar únicamente los archivos PDF
pdfs = []

# Recorrer todos los elementos encontrados en la carpeta docs/
for f in archivos:
    # Verificar si el archivo termina en ".pdf"
    # Solo esos archivos nos interesan para este proyecto
    if f.endswith(".pdf"):
        # Agregar el nombre del archivo PDF a la lista
        pdfs.append(f)

        # Imprimir el nombre del PDF encontrado
        print(f)

# Ordenar alfabéticamente la lista de PDFs
# Esto hace que el script siempre elija el mismo primer archivo
pdfs_ordenados = sorted(pdfs)

# Tomar el primer PDF de la lista ordenada
primer_pdf = pdfs_ordenados[0]

# Construir la ruta completa del archivo PDF
# Une la carpeta docs/ con el nombre del archivo
ruta_completa = os.path.join(DOCS_DIR, primer_pdf)

# Abrir el PDF usando PdfReader
# Esto crea un objeto que permite acceder a sus páginas y extraer texto
reader = PdfReader(ruta_completa)

# Mostrar el nombre del PDF que se está leyendo
print(f"📄 {primer_pdf}")

# Mostrar cuántas páginas tiene el PDF
# reader.pages contiene todas las páginas del documento
print(f"   Páginas: {len(reader.pages)}")

# Mostrar un texto de referencia para indicar lo que viene
print(f"   Texto de la primera página:")

# Extraer e imprimir el texto de la primera página
# reader.pages[0] accede a la primera página
# .extract_text() intenta obtener el texto legible de esa página
print(reader.pages[0].extract_text())

print("------------------------------------")


def extract_pdf(pdf_path):
    
    #Recibir la ruta de un pdf
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOCS_DIR = os.path.join(BASE_DIR, "..", pdf_path)
    archivos = os.listdir(DOCS_DIR)
    pdfs = []
    for f in archivos:
        if f.endswith(".pdf"):
            pdfs.append(f)
    pdfs_ordenados = sorted(pdfs)
    
    for p in pdfs_ordenados:
        pdf_seleccionado = pdfs_ordenados[p]
        ruta_completa = os.path.join(DOCS_DIR, pdf_seleccionado)
        reader = PdfReader(ruta_completa)
        paginas = len(reader.pages)
        print(f"📄 {pdf_seleccionado}")
        print(f"   Páginas: {paginas}")
        
        print(reader.pages[0].extract_text())
        
    #Crear un PdfReader
    
    
    #recorrer reader.pages
    
    
    #concatenar el texto
    
    
    #devolver el texto completo


pdfs = extract_pdf("docs")
print(pdfs)

