import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from sqlalchemy import select
from config.db import SessionLocal
from models.faq import faq


RUTA_VECTORSTORE = "vectorstore"
RUTA_FAQ = "vectorstore_faq"

os.makedirs(RUTA_VECTORSTORE, exist_ok=True)
os.makedirs(RUTA_FAQ, exist_ok=True)

modelo_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

divisor_texto = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)



def obtener_ruta_indice_usuario(id_usuario: int):
    return os.path.join(RUTA_VECTORSTORE, f"usuario_{id_usuario}")

def cargar_vectorstore_usuario(user_id: int):
    ruta = obtener_ruta_indice_usuario(user_id)

    if os.path.exists(ruta):
        return FAISS.load_local(
            ruta,
            modelo_embeddings,
            allow_dangerous_deserialization=True
        )

    return None

def guardar_vectorstore_usuario(user_id: int, vectorstore: FAISS):
    ruta = obtener_ruta_indice_usuario(user_id)
    vectorstore.save_local(ruta)

def agregar_pdf_a_usuario(user_id: int, texto_pdf: str, nombre_archivo: str):

    fragmentos = divisor_texto.split_text(texto_pdf)

    documentos = [
        Document(
            page_content=fragmento,
            metadata={
                "id_usuario": user_id,
                "nombre_archivo": nombre_archivo
            }
        )
        for fragmento in fragmentos
    ]

    vectorstore = cargar_vectorstore_usuario(user_id)

    if vectorstore:
        vectorstore.add_documents(documentos)
    else:
        vectorstore = FAISS.from_documents(documentos, modelo_embeddings)

    guardar_vectorstore_usuario(user_id, vectorstore)

    return len(fragmentos)

def buscar_en_documentos_usuario(user_id: int, query: str, k: int = 5):

    vectorstore = cargar_vectorstore_usuario(user_id)

    if not vectorstore:
        return []

    resultados = vectorstore.similarity_search(
        query,
        k=k,
        filter={"id_usuario": user_id}
    )

    return resultados




def construir_indice_faq():
    db = SessionLocal()

    try:
        stmt = select(faq)
        resultados = db.execute(stmt).fetchall()

        documentos = []

        for row in resultados:
            data = dict(row._mapping)

            contenido = f"""
Pregunta: {data.get('pregunta')}
Respuesta: {data.get('respuesta')}
"""

            documentos.append(
                Document(
                    page_content=contenido,
                    metadata={"faq_id": data.get("id")}
                )
            )

        if not documentos:
            return None

        vectorstore = FAISS.from_documents(documentos, modelo_embeddings)
        vectorstore.save_local(RUTA_FAQ)

        return vectorstore

    finally:
        db.close()


def cargar_indice_faq():
    if os.path.exists(RUTA_FAQ):
        return FAISS.load_local(
            RUTA_FAQ,
            modelo_embeddings,
            allow_dangerous_deserialization=True
        )

    return construir_indice_faq()


def buscar_faq(pregunta: str, k: int = 1, threshold: float = 0.75) -> str:

    vectorstore = cargar_indice_faq()

    if not vectorstore:
        return ""

    resultados = vectorstore.similarity_search_with_score(
        pregunta,
        k=k
    )

    if not resultados:
        return ""

    mejor_doc, score = resultados[0]

    if score > threshold:
        return ""

    return mejor_doc.page_content