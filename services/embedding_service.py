from sentence_transformers import SentenceTransformer
from config.queries import get_faq_data
import numpy as np

model = None
rows = []
embeddings = None

def init_embeddings():
    global model, rows, embeddings

    if model is not None:
        return

    print("Cargando modelo...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Cargando FAQs...")
    rows = get_faq_data()

    sentences = [
        f"Pregunta: {row.pregunta} Respuesta: {row.respuesta}"
        for row in rows
    ]

    if sentences:
        embeddings = model.encode(sentences)
    else:
        embeddings = np.array([])

    print("Embeddings listos:", len(embeddings))


def buscar_faq(texto_usuario: str):
    """Busca la FAQ más relevante para el texto del usuario"""
    global model, embeddings, rows

    if model is None:
        init_embeddings()

    if embeddings is None or len(embeddings) == 0:
        return "No hay FAQs disponibles."

    embedding_usuario = model.encode([texto_usuario])[0]

    similitudes = np.dot(embeddings, embedding_usuario) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(embedding_usuario)
    )

    idx_max = np.argmax(similitudes)
    return rows[idx_max].respuesta


def buscar_en_embeddings(texto_usuario: str):
    """Función genérica para buscar cualquier embedding cargado"""
    global model, embeddings, rows

    if model is None:
        init_embeddings()

    if embeddings is None or len(embeddings) == 0:
        return []

    embedding_usuario = model.encode([texto_usuario])[0]

    similitudes = np.dot(embeddings, embedding_usuario) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(embedding_usuario)
    )

    idx_max = np.argmax(similitudes)
    return [rows[idx_max].respuesta]  # Retorna lista para compatibilidad con otros servicios
