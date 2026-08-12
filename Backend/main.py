from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path

from .hybrid_rag import hybrid_rag
from .vector_search import (
    add_documents_to_faiss,
    get_indexed_sources,
    delete_document_from_faiss,
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
    version="1.0",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = BASE_DIR / "data" / "documents"

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# REQUEST MODELS
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Hybrid RAG Chatbot API is running",
        "status": "healthy",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    try:

        answer = hybrid_rag(question)

        return {
            "question": question,
            "answer": answer,
        }

    except Exception as e:

        print(
            f"Error while processing question: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}",
        )


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
            detail="No filename provided",
        )

    # Remove any path information
    safe_filename = Path(file.filename).name

    if not safe_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    # --------------------------------------------------------
    # Allowed file types
    # --------------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".json",
    }

    extension = Path(
        safe_filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed: PDF, DOCX, TXT, JSON"
            ),
        )

    # --------------------------------------------------------
    # File path
    # --------------------------------------------------------

    file_path = DOCUMENTS_DIR / safe_filename

    # --------------------------------------------------------
    # Check duplicate
    # --------------------------------------------------------

    if file_path.exists():

        raise HTTPException(
            status_code=409,
            detail=(
                f"Document already exists: "
                f"{safe_filename}"
            ),
        )

    # --------------------------------------------------------
    # Save file
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
            detail=(
                f"Failed to save document: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Add document to FAISS
    # --------------------------------------------------------

    try:

        # IMPORTANT:
        # This uses the function that you actually imported:
        #
        # add_documents_to_faiss
        #
        # If your vector_search.py expects a list of files,
        # change this to:
        #
        # add_documents_to_faiss([file_path])

        result = add_documents_to_faiss(
            file_path
        )

        print(
            f"FAISS indexing result: {result}"
        )

    except Exception as e:

        # Remove physical file if indexing failed

        if file_path.exists():
            file_path.unlink()

        print(
            f"FAISS indexing failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to index document: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Determine chunks added
    # --------------------------------------------------------

    if isinstance(result, int):
        chunks_added = result
    else:
        chunks_added = 0

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Document uploaded and indexed "
            "successfully"
        ),
        "filename": safe_filename,
        "chunks_added": chunks_added,
    }


# ============================================================
# LIST DOCUMENTS
# ============================================================

@app.get("/documents")
def list_documents():

    try:

        documents = get_indexed_sources()

        # Make sure the response is always a list
        if documents is None:
            documents = []

        return {
            "documents": documents,
            "count": len(documents),
        }

    except Exception as e:

        print(
            f"Error while listing documents: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to retrieve documents: {str(e)}"
            ),
        )


# ============================================================
# DELETE DOCUMENT
# ============================================================

@app.delete("/documents/{filename}")
def delete_document(filename: str):

    # --------------------------------------------------------
    # Prevent path traversal
    # --------------------------------------------------------

    safe_filename = Path(filename).name

    if not safe_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    file_path = DOCUMENTS_DIR / safe_filename

    # --------------------------------------------------------
    # Delete from FAISS
    # --------------------------------------------------------

    try:

        deleted_chunks = delete_document_from_faiss(
            safe_filename
        )

    except Exception as e:

        print(
            f"FAISS delete failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to delete document "
                f"from FAISS: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    file_deleted = False

    if file_path.exists():

        try:

            file_path.unlink()

            file_deleted = True

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to delete physical "
                    f"file: {str(e)}"
                ),
            )

    # --------------------------------------------------------
    # Document not found
    # --------------------------------------------------------

    if deleted_chunks == 0 and not file_deleted:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Document deleted successfully"
        ),
        "filename": safe_filename,
        "deleted_chunks": deleted_chunks,
        "file_deleted": file_deleted,
    }