from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from pydantic import BaseModel

from pathlib import Path
import shutil

from .hybrid_rag import hybrid_rag

from .data_ingestion import ingest_file

from .vector_search import (
    add_documents_to_faiss,
    get_indexed_sources,
    delete_document_from_faiss
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Hybrid RAG Chatbot",
    description=(
        "Hybrid RAG using FAISS, Neo4j, "
        "LangChain and OpenAI"
    ),
    version="1.0"
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = (
    BASE_DIR
    / "data"
    / "documents"
)

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message":
        "Hybrid RAG Chatbot API is running"
    }


# ============================================================
# CHAT / ASK
# ============================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    answer = hybrid_rag(
        request.question
    )

    return {

        "question":
        request.question,

        "answer":
        answer
    }
@app.delete("/documents/{filename}")

# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    filename = file.filename

    # --------------------------------------------------------
    # Allowed file types
    # --------------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".json"
    }

    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed: PDF, DOCX, TXT, JSON"
            )
        )

    # --------------------------------------------------------
    # Prevent path traversal
    # --------------------------------------------------------

    safe_filename = Path(filename).name

    file_path = DOCUMENTS_DIR / safe_filename

    # --------------------------------------------------------
    # Check duplicate file
    # --------------------------------------------------------

    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Document already exists: {safe_filename}"
        )

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    try:

        contents = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        print(
            f"Uploaded document: {safe_filename}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document: {str(e)}"
        )

    # --------------------------------------------------------
    # Add document to FAISS
    # --------------------------------------------------------

    try:

        chunks_added = add_document_to_faiss(
            file_path
        )

        print(
            f"FAISS chunks added: {chunks_added}"
        )

    except Exception as e:

        # If indexing fails, remove the physical file
        # so the system does not show an unindexed document.

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to index document: {str(e)}"
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "message":
            "Document uploaded and indexed successfully",

        "filename":
            safe_filename,

        "chunks_added":
            chunks_added
    }
# ============================================================
# LIST DOCUMENTS
# ============================================================

@app.get("/documents")
def list_documents():

    documents = get_indexed_sources()

    return {
        "documents": documents
    }

# ============================================================
# GET DOCUMENT LIST
# ============================================================

@app.get("/documents")
def get_documents():

    files = []

    if DOCUMENTS_DIR.exists():

        for file_path in DOCUMENTS_DIR.iterdir():

            if file_path.is_file():

                files.append(file_path.name)

    return {
        "documents": sorted(files)
    }

# ============================================================
# DELETE DOCUMENT
# ============================================================

@app.delete("/documents/{filename}")
def delete_document(filename: str):

    file_path = DOCUMENTS_DIR / filename

    # --------------------------------------------------------
    # Delete from FAISS
    # --------------------------------------------------------

    deleted_chunks = delete_document_from_faiss(
        filename
    )

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    file_deleted = False

    if file_path.exists():

        file_path.unlink()

        file_deleted = True


    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    if deleted_chunks == 0 and not file_deleted:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    return {

        "message":
            "Document deleted successfully",

        "filename":
            filename,

        "deleted_chunks":
            deleted_chunks,

        "file_deleted":
            file_deleted
    }