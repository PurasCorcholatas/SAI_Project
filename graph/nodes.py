from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings

class LocalEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v12"
        )

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()

embeddings = LocalEmbeddings()

vectorstore = FAISS.load_local(
    "rag/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

def buscar_faq(query: str, k: int = 3) -> str:
    docs = vectorstore.similarity_search(query, k=k)

    if not docs:
        return ""

    return "\n\n".join(doc.page_content for doc in docs)
