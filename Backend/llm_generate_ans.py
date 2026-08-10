import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def generate_answer(question: str, context: dict):

    # --------------------------------
    # Format Neo4j context
    # --------------------------------

    graph_context = ""

    for item in context["graph_context"]:

        graph_context += f"{item}\n"


    # --------------------------------
    # Format FAISS context
    # --------------------------------

    vector_context = ""

    for item in context["vector_context"]:

        vector_context += (
            f"Content: {item['content']}\n"
            f"Source: {item['metadata'].get('source')}\n"
            f"Page: {item['metadata'].get('page')}\n\n"
        )


    # --------------------------------
    # Create final context
    # --------------------------------

    final_context = f"""
GRAPH INFORMATION:
{graph_context}

DOCUMENT INFORMATION:
{vector_context}
"""


    # --------------------------------
    # LLM Prompt
    # --------------------------------

    prompt = f"""
You are a helpful Hybrid RAG assistant.

Answer the user's question using the provided
Graph Information and Document Information.

Rules:

1. Use the provided context as the primary source.
2. Do not invent information.
3. If the context does not contain enough information,
   clearly say that the information is not available.
4. Give a concise and direct answer.
5. When useful, mention the source page.

Context:
{final_context}

User Question:
{question}

Answer:
"""


    # --------------------------------
    # Generate answer
    # --------------------------------

    response = llm.invoke(prompt)

    return response.content