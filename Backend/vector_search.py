from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FAISS_PATH = BASE_DIR / "data" / "faiss_index"


# --------------------------------
# Load embedding model
# --------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# Embedding wrapper
# --------------------------------

class SentenceTransformerEmbeddings(Embeddings):

    def embed_documents(self, texts):
        return model.encode(texts).tolist()

    def embed_query(self, text):
        return model.encode([text])[0].tolist()


embedding_function = SentenceTransformerEmbeddings()


# --------------------------------
# Load saved FAISS index
# --------------------------------

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FAISS_PATH = BASE_DIR / "data" / "faiss_index"

vector_store = FAISS.load_local(
    str(FAISS_PATH),
    embedding_function,
    allow_dangerous_deserialization=True
)
print("FAISS index loaded successfully!")


# --------------------------------
# Vector search
# --------------------------------

def vector_search(question: str, top_k: int = 2):

    results = vector_store.similarity_search(
        question,
        k=top_k
    )

    return results
