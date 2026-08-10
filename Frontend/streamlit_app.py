import streamlit as st
import requests


# --------------------------------
# Page configuration
# --------------------------------

st.set_page_config(
    page_title="Hybrid RAG Chatbot",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------
# Title
# --------------------------------

st.title("🤖 Hybrid RAG Chatbot")

st.write(
    "Ask questions about the knowledge base."
)


# --------------------------------
# FastAPI URL
# --------------------------------

import os

API_URL = os.getenv(
    "API_URL",
    "http://backend:8000/chat"
)


# --------------------------------
# Chat history
# --------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------
# Display previous messages
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# --------------------------------
# Chat input
# --------------------------------

question = st.chat_input(
    "Ask a question..."
)


# --------------------------------
# Process question
# --------------------------------

if question:

    # Show user question

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.write(question)


    # --------------------------------
    # Call FastAPI
    # --------------------------------

    try:

        response = requests.post(
            API_URL,
            json={
                "question": question
            },
            timeout=60
        )


        if response.status_code == 200:

            data = response.json()

            answer = data["answer"]


        else:

            answer = (
                f"API Error: {response.status_code}\n\n"
                f"{response.text}"
            )


    except requests.exceptions.RequestException as e:

        answer = f"Unable to connect to FastAPI: {e}"


    # --------------------------------
    # Display answer
    # --------------------------------

    with st.chat_message("assistant"):

        st.write(answer)


    # Save answer

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })