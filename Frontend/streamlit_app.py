import os
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)

CHAT_URL = f"{API_URL}/ask"
DOCUMENTS_URL = f"{API_URL}/documents"
UPLOAD_URL = f"{API_URL}/upload-document"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Knowledge Base Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SIMPLE STREAMLIT STYLING
# No custom HTML
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #f5f7fb;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #172554;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 8px;
    }

    /* Main title */
    .main-title {
        font-size: 34px;
        font-weight: 700;
        color: #172554;
    }

    /* Subtitle */
    .main-subtitle {
        font-size: 17px;
        color: #64748b;
        margin-bottom: 20px;
    }

    /* Status cards */
    .status-card {
        padding: 20px;
        border-radius: 12px;
        background-color: white;
        border: 1px solid #e2e8f0;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "documents" not in st.session_state:
    st.session_state.documents = []

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# API HELPERS
# ============================================================

def get_documents():
    """Get documents from FastAPI."""

    try:
        response = requests.get(
            DOCUMENTS_URL,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        # Handle different possible API response formats
        if isinstance(data, list):
            documents = data

        elif isinstance(data, dict):
            documents = (
                data.get("documents")
                or data.get("files")
                or data.get("sources")
                or []
            )

        else:
            documents = []

        # Normalize document names
        normalized = []

        for item in documents:

            if isinstance(item, str):
                normalized.append(item)

            elif isinstance(item, dict):

                name = (
                    item.get("filename")
                    or item.get("name")
                    or item.get("source")
                )

                if name:
                    normalized.append(name)

        return sorted(
            list(set(normalized)),
            key=str.lower
        )

    except requests.exceptions.RequestException as e:

        st.sidebar.error(
            f"Unable to connect to FastAPI.\n\n{e}"
        )

        return []


def upload_document(uploaded_file):

    try:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        response = requests.post(
            UPLOAD_URL,
            files=files,
            timeout=300
        )

        response.raise_for_status()

        return True, response.json()

    except requests.exceptions.RequestException as e:

        return False, str(e)


def delete_document(filename):

    try:

        response = requests.delete(
            f"{DOCUMENTS_URL}/{filename}",
            timeout=120
        )

        response.raise_for_status()

        return True, response.json()

    except requests.exceptions.RequestException as e:

        return False, str(e)


def ask_question(question):

    try:

        response = requests.post(
            CHAT_URL,
            json={
                "question": question
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "answer",
            "No answer returned."
        )

    except requests.exceptions.RequestException as e:

        return (
            "Unable to connect to FastAPI.\n\n"
            f"Error: {e}"
        )


# ============================================================
# INITIAL DOCUMENT LOAD
# ============================================================

if not st.session_state.documents:

    st.session_state.documents = get_documents()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 📚 Knowledge Base")

    st.caption(
        "Upload and manage your knowledge documents."
    )

    st.divider()

    # --------------------------------------------------------
    # Browse Documents
    # --------------------------------------------------------

    st.subheader("📤 Browse Documents")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=[
            "pdf",
            "docx",
            "txt",
            "json"
        ],
        help="Supported files: PDF, DOCX, TXT and JSON"
    )

    if uploaded_file is not None:

        st.info(
            f"Selected: {uploaded_file.name}"
        )

        if st.button(
            "🚀 Upload & Index",
            use_container_width=True
        ):

            with st.spinner(
                "Uploading and indexing document..."
            ):

                success, result = upload_document(
                    uploaded_file
                )

            if success:

                st.success(
                    "Document uploaded and indexed successfully."
                )

                # Refresh document list
                st.session_state.documents = get_documents()

                # Clear uploader on next rerun
                st.rerun()

            else:

                st.error(
                    f"Upload failed:\n\n{result}"
                )

    st.divider()

    # --------------------------------------------------------
    # Uploaded Documents
    # --------------------------------------------------------

    st.subheader("📁 Uploaded Documents")

    documents = st.session_state.documents

    if documents:

        st.caption(
            f"{len(documents)} document(s) available"
        )

    else:

        st.caption(
            "No documents available."
        )

    # --------------------------------------------------------
    # Document list
    # --------------------------------------------------------

    for index, filename in enumerate(documents):

        with st.container(border=True):

            st.write(
                f"📄 **{filename}**"
            )

            if st.button(
                "🗑️ Delete",
                key=f"delete_{index}_{filename}",
                use_container_width=True
            ):

                # Confirmation
                st.session_state[
                    "delete_target"
                ] = filename

                st.rerun()


    # --------------------------------------------------------
    # Delete confirmation
    # --------------------------------------------------------

    if "delete_target" in st.session_state:

        filename = st.session_state[
            "delete_target"
        ]

        st.warning(
            f"Delete **{filename}**?"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Yes",
                key="confirm_delete",
                use_container_width=True
            ):

                with st.spinner(
                    "Deleting document..."
                ):

                    success, result = delete_document(
                        filename
                    )

                if success:

                    st.success(
                        "Document deleted successfully."
                    )

                    st.session_state.documents = (
                        get_documents()
                    )

                    del st.session_state[
                        "delete_target"
                    ]

                    st.rerun()

                else:

                    st.error(
                        f"Delete failed:\n\n{result}"
                    )

        with col2:

            if st.button(
                "Cancel",
                key="cancel_delete",
                use_container_width=True
            ):

                del st.session_state[
                    "delete_target"
                ]

                st.rerun()

    st.divider()

    # --------------------------------------------------------
    # Refresh
    # --------------------------------------------------------

    if st.button(
        "🔄 Refresh Documents",
        use_container_width=True
    ):

        st.session_state.documents = get_documents()

        st.rerun()

    st.divider()

    st.caption(
        "💡 Supported files"
    )

    st.caption(
        "PDF • DOCX • TXT • JSON"
    )


# ============================================================
# MAIN PAGE
# ============================================================

st.title("🤖 Knowledge Base Assistant")

st.caption(
    "Ask questions across your company knowledge base "
    "using FAISS + Neo4j + LangChain + LLM."
)

# ============================================================
# STATUS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label="📄 Documents",
        value=len(st.session_state.documents)
    )

with col2:

    st.metric(
        label="🔎 Vector Search",
        value="FAISS"
    )

with col3:

    st.metric(
        label="🕸️ Graph Search",
        value="Neo4j"
    )


st.divider()


# ============================================================
# CURRENT KNOWLEDGE BASE
# ============================================================

st.subheader(
    "📚 Current Knowledge Base"
)

if st.session_state.documents:

    # Show documents in columns
    number_of_columns = 3

    document_columns = st.columns(
        number_of_columns
    )

    for index, filename in enumerate(
        st.session_state.documents
    ):

        column = document_columns[
            index % number_of_columns
        ]

        with column:

            with st.container(border=True):

                st.write("📄")

                st.write(
                    f"**{filename}**"
                )

else:

    st.info(
        "No documents are currently indexed."
    )


st.divider()


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.messages:

    st.subheader("💬 Conversation")

    for message in st.session_state.messages:

        if message["role"] == "user":

            with st.chat_message(
                "user"
            ):

                st.write(
                    message["content"]
                )

        else:

            with st.chat_message(
                "assistant"
            ):

                st.write(
                    message["content"]
                )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about your knowledge base..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.write(question)

    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner(
            "Searching your knowledge base..."
        ):

            answer = ask_question(
                question
            )

        st.write(answer)

    # Store assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )