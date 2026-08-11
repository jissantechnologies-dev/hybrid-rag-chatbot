from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FAISS_PATH = BASE_DIR / "data" / "faiss_index"


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully!")


# ============================================================
# EMBEDDING WRAPPER
# ============================================================

class SentenceTransformerEmbeddings(Embeddings):

    def embed_documents(self, texts):
        return model.encode(texts).tolist()

    def embed_query(self, text):
        return model.encode([text])[0].tolist()


embedding_function = SentenceTransformerEmbeddings()


# ============================================================
# LOAD FAISS INDEX
# ============================================================

print("Loading FAISS index...")

vector_store = FAISS.load_local(
    str(FAISS_PATH),
    embedding_function,
    allow_dangerous_deserialization=True
)

print("FAISS index loaded successfully!")


# ============================================================
# VECTOR SEARCH
# ============================================================

def vector_search(question: str, top_k: int = 3):

    return vector_store.similarity_search(
        question,
        k=top_k
    )


# ============================================================
# GET INDEXED SOURCES
# ============================================================

def get_indexed_sources():

    sources = set()

    for document in vector_store.docstore._dict.values():

        source = document.metadata.get("source")

        if source:
            sources.add(source)

    return sorted(sources)


# ============================================================
# ADD DOCUMENTS TO FAISS
# ============================================================

def add_documents_to_faiss(documents):

    global vector_store

    if not documents:
        return

    vector_store.add_documents(documents)

    vector_store.save_local(
        str(FAISS_PATH)
    )

    print(
        f"Added {len(documents)} documents to FAISS."
    )


# ============================================================
# DELETE ONE DOCUMENT SOURCE FROM FAISS
# ============================================================

def delete_document_from_faiss(source_filename: str):
    global vector_store

    print(f"\nDeleting from FAISS: {source_filename}")

    # --------------------------------------------------------
    # Find FAISS document IDs belonging to this source
    # --------------------------------------------------------

    ids_to_delete = []

    for doc_id, document in vector_store.docstore._dict.items():

        source = document.metadata.get("source")

        if source == source_filename:
            ids_to_delete.append(doc_id)

    # --------------------------------------------------------
    # Nothing found
    # --------------------------------------------------------

    if not ids_to_delete:

        print(
            f"No FAISS chunks found for: {source_filename}"
        )

        return 0

    print(
        f"FAISS chunks found: {len(ids_to_delete)}"
    )

    # --------------------------------------------------------
    # Delete from FAISS
    # --------------------------------------------------------

    vector_store.delete(ids_to_delete)

    # --------------------------------------------------------
    # Save updated FAISS index
    # --------------------------------------------------------

    vector_store.save_local(
        str(FAISS_PATH)
    )

    print(
        f"FAISS chunks deleted: {len(ids_to_delete)}"
    )

    print(
        f"Updated FAISS index saved to: {FAISS_PATH}"
    )

    return len(ids_to_delete)

# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def remove_documents_from_faiss(
    source_filename: str
):

    return delete_document_from_faiss(
        source_filename
    )