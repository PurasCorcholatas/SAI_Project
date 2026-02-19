
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document



VECTORSTORE_PATH = "vectorstore"


os.makedirs(VECTORSTORE_PATH, exist_ok=True)


embeddings = HuggingFaceEmbeddings()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

def get_user_index_path(user_id: int):
    """Devuelve la ruta de FAISS para un usuario"""
    path = os.path.join(VECTORSTORE_PATH, f"user_{user_id}.faiss")
    return path

def load_user_vectorstore(user_id: int):
    """Carga FAISS del usuario si existe, si no devuelve None"""
    path = get_user_index_path(user_id)
    if os.path.exists(path):
        return FAISS.load_local(path, embeddings)
    return None

def save_user_vectorstore(user_id: int, vectorstore: FAISS):
    """Guarda FAISS del usuario"""
    path = get_user_index_path(user_id)
    vectorstore.save_local(path)

def add_pdf_to_user(user_id: int, pdf_text: str, metadata: dict = None):
    """Divide texto, genera embeddings y guarda en FAISS del usuario"""
    metadata = metadata or {}
    chunks = text_splitter.split_text(pdf_text)
    docs = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]

    vectorstore = load_user_vectorstore(user_id)
    if vectorstore:
        vectorstore.add_documents(docs)
    else:
        vectorstore = FAISS.from_documents(docs, embeddings)
    
    save_user_vectorstore(user_id, vectorstore)
    return len(chunks)

def search_user_vectorstore(user_id: int, query: str, k: int = 5):
    """Busca en FAISS del usuario"""
    vectorstore = load_user_vectorstore(user_id)
    if not vectorstore:
        return []
    results = vectorstore.similarity_search(query, k=k)
    return results
