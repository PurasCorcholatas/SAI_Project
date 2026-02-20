# from pathlib import Path
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from config.queries import get_faq_data


# BASE_DIR = Path(__file__).resolve().parent
# FAISS_PATH = BASE_DIR / "faiss_index"


# embeddings = HuggingFaceEmbeddings(
#     model_name="distiluse-base-multilingual-cased-v2"
# )


# rows = get_faq_data()

# texts = [
#     f"Pregunta: {row.pregunta}\nRespuesta: {row.respuesta}"
#     for row in rows
# ]


# vectorstore = FAISS.from_texts(
#     texts=texts,
#     embedding=embeddings
# )

# vectorstore.save_local(FAISS_PATH)

# print(" Índice FAISS creado correctamente")
# print(" Guardado en:", FAISS_PATH)
