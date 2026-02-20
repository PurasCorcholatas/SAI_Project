# import os
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from sqlalchemy.orm import Session
# from models.documento_telegram import documentos_telegram
# from config.queries import get_faq_data



# VECTORSTORE_PATH = "vectorstore/faiss_index"

# embeddings_model = OpenAIEmbeddings(
#     model="text-embedding-3-small"
# )

# vectorstore = None




# def init_vectorstore():
#     """
#     Inicializa el índice FAISS.
#     - Si existe en disco, lo carga.
#     - Si no existe, lo crea con FAQs (si hay).
#     """

#     global vectorstore

    
#     if vectorstore is not None:
#         return

    
#     if os.path.exists(VECTORSTORE_PATH):
#         vectorstore = FAISS.load_local(
#             VECTORSTORE_PATH,
#             embeddings_model,
#             allow_dangerous_deserialization=True
#         )
#         print("Vectorstore cargado desde disco.")
#         return

    
#     print("Creando nuevo vectorstore...")

#     faq_rows = get_faq_data()

#     textos = [
#         f"Pregunta: {row.pregunta}\nRespuesta: {row.respuesta}"
#         for row in faq_rows
#     ]

#     if textos:
#         metadatas = [{"tipo": "faq"} for _ in textos]

#         vectorstore = FAISS.from_texts(
#             textos,
#             embeddings_model,
#             metadatas=metadatas
#         )

#         vectorstore.save_local(VECTORSTORE_PATH)
#         print("FAQs indexadas correctamente.")
#     else:
        
#         vectorstore = FAISS.from_texts(
#             ["Inicializando índice vacío"],
#             embeddings_model,
#             metadatas=[{"tipo": "init"}]
#         )
#         vectorstore.save_local(VECTORSTORE_PATH)
#         print("Vectorstore creado vacío.")




# def buscar_faq(texto_usuario: str):
#     """
#     Busca la FAQ más relevante.
#     """

#     global vectorstore
#     init_vectorstore()

#     resultados = vectorstore.similarity_search(
#         texto_usuario,
#         k=1,
#         filter={"tipo": "faq"}
#     )

#     if not resultados:
#         return ""

#     return resultados[0].page_content




# def guardar_documento_embeddings(user_id: int, chunks: list[str]):
#     """
#     Guarda chunks de un PDF asociados a un usuario.
#     """

#     global vectorstore
#     init_vectorstore()

#     if not chunks:
#         return False

#     metadatas = [
#         {
#             "tipo": "documento",
#             "user_id": int(user_id)
#         }
#         for _ in chunks
#     ]

#     vectorstore.add_texts(
#         texts=chunks,
#         metadatas=metadatas
#     )

#     vectorstore.save_local(VECTORSTORE_PATH)

#     print(f"Documento del usuario {user_id} guardado.")
#     return True




# def buscar_documentos_usuario(texto_usuario: str, user_id: int, k: int = 3):
#     """
#     Busca información SOLO en documentos del usuario.
#     """

#     global vectorstore
#     init_vectorstore()

#     resultados = vectorstore.similarity_search(
#         texto_usuario,
#         k=k,
#         filter={
#             "tipo": "documento",
#             "user_id": int(user_id)
#         }
#     )

#     if not resultados:
#         return ""

#     return "\n\n".join([doc.page_content for doc in resultados])



# # def eliminar_documento_completo(nombre_archivo: str, user_id: int, db: Session):
   

# #     global vectorstore
# #     init_vectorstore()

# #     #
# #     documentos = db.query(documentos_telegram).filter(
# #         documentos_telegram.nombre_original == nombre_archivo,
# #         documentos_telegram.id_usuario == user_id
# #     ).all()

# #     for doc in documentos:
# #         if os.path.exists(doc.ruta_archivo):
# #             os.remove(doc.ruta_archivo)
# #             print(f"Archivo eliminado: {doc.ruta_archivo}")

# #         db.delete(doc)

# #     db.commit()
# #     print("Registros eliminados de la BD.")

# #     # 2️⃣ Embeddings
# #     all_docs = vectorstore.similarity_search("", k=10000)

# #     docs_filtrados = []

# #     for doc in all_docs:
# #         if not (
# #             doc.metadata.get("tipo") == "documento"
# #             and doc.metadata.get("user_id") == user_id
# #         ):
# #             docs_filtrados.append(doc)

# #     textos = [doc.page_content for doc in docs_filtrados]
# #     metadatas = [doc.metadata for doc in docs_filtrados]

# #     vectorstore = FAISS.from_texts(
# #         textos,
# #         embeddings_model,
# #         metadatas=metadatas
# #     )

# #     vectorstore.save_local(VECTORSTORE_PATH)

# #     print("Embeddings eliminados correctamente.")