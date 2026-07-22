import chromadb

CHROMA_DIR = "src/chroma_db"
COLLECTION_NAME = "rag_documents"

client = chromadb.PersistentClient(path=CHROMA_DIR)

try:
    collection = client.get_collection(name=COLLECTION_NAME)
    print("La colección existe.")
    print("Cantidad de registros:", collection.count())
except Exception as e:
    print("La colección NO existe todavía.")
    print("Detalle:", e)

print("Colecciones disponibles:")
for c in client.list_collections():
    print("-", c.name)