from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent
FAISS_PATH = BASE_DIR / "faiss_index"


embeddings = HuggingFaceEmbeddings(
    model_name="distiluse-base-multilingual-cased-v2"
)


vectorstore = FAISS.load_local(
    FAISS_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

print("FAISS cargado correctamente")


def buscar_faq(pregunta: str) -> str:
    docs = vectorstore.similarity_search(pregunta, k=1)

    if not docs:
        return "No encontré una respuesta relacionada."

    return docs[0].page_content

def buscar_en_embeddings(pregunta: str, k: int = 3):
    """
    Busca en el índice FAISS y devuelve los k documentos más relevantes.
    """
    docs = vectorstore.similarity_search(pregunta, k=k)
    return [d.page_content for d in docs]
