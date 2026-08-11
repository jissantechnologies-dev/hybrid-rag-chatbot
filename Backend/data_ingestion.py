import json
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)

from langchain_core.documents import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = (
    BASE_DIR
    / "data"
    / "documents"
)


# ============================================================
# TEXT SPLITTER
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


# ============================================================
# LOAD SINGLE FILE
# ============================================================

def load_document(file_path):

    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    print(
        f"Processing: {file_path.name}"
    )


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == ".pdf":

        loader = PyPDFLoader(
            str(file_path)
        )

        documents = loader.load()

        for document in documents:

            document.metadata["source"] = (
                file_path.name
            )

            document.metadata["file_type"] = "pdf"

        return documents


    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    elif extension == ".docx":

        loader = Docx2txtLoader(
            str(file_path)
        )

        documents = loader.load()

        for document in documents:

            document.metadata["source"] = (
                file_path.name
            )

            document.metadata["file_type"] = "docx"

        return documents


    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    elif extension == ".txt":

        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        documents = loader.load()

        for document in documents:

            document.metadata["source"] = (
                file_path.name
            )

            document.metadata["file_type"] = "txt"

        return documents


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    elif extension == ".json":

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            json_data = json.load(file)


        json_text = json.dumps(
            json_data,
            indent=2,
            ensure_ascii=False
        )


        document = Document(
            page_content=json_text,
            metadata={
                "source": file_path.name,
                "file_type": "json"
            }
        )

        return [document]


    # --------------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported file type: "
            f"{extension}"
        )


# ============================================================
# INGEST ONE FILE
# ============================================================

def ingest_file(file_path):

    print(
        f"\nLoading document: "
        f"{file_path}"
    )


    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    documents = load_document(
        file_path
    )

    print(
        f"Loaded {len(documents)} sections"
    )


    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    chunks = text_splitter.split_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks"
    )


    return chunks