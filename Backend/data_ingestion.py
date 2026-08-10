from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer



from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PDF_PATH = BASE_DIR / "data" / "sample_apple_knowledge_base.pdf"

FAISS_PATH = BASE_DIR / "data" / "faiss_index"

# --------------------------------
# Step 1: Load PDF
# --------------------------------

loader = PyPDFLoader(PDF_PATH)

documents = loader.load()

print("PDF loaded successfully!")
print("Number of pages:", len(documents))


# --------------------------------
# Step 2: Split documents
# --------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents)


print("\nPDF split successfully!")
print("Number of chunks:", len(chunks))

# --------------------------------
# Step 3: Load embedding model
# --------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

print("\nEmbedding model loaded successfully!")

# --------------------------------
# Step 4: Generate embeddings
# --------------------------------

texts = [chunk.page_content for chunk in chunks]

embeddings = model.encode(texts)

print("Embeddings generated successfully!")

print("Number of embeddings:", len(embeddings))

print("Embedding dimension:", embeddings.shape[1])


# --------------------------------
# Step 5: Create LangChain
# compatible embedding class
# --------------------------------

class SentenceTransformerEmbeddings(Embeddings):

    def embed_documents(self, texts):
        return model.encode(texts).tolist()

    def embed_query(self, text):
        return model.encode([text])[0].tolist()


embedding_function = SentenceTransformerEmbeddings()


# --------------------------------
# Step 6: Create FAISS vector store
# --------------------------------

vector_store = FAISS.from_documents(
    chunks,
    embedding_function
)

print("\nFAISS vector store created successfully!")


# --------------------------------
# Step 7: Save FAISS index
# --------------------------------

vector_store.save_local(FAISS_PATH)

print(f"FAISS index saved to: {FAISS_PATH}")