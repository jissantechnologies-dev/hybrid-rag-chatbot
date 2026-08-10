import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def classify_question(question: str):

    prompt = f"""
You are a query router for a Hybrid RAG system.

Identify which retrieval categories are needed to answer
the user's question.

Available categories:

- founder
- ceo
- product
- general

A question can have MORE THAN ONE category.

Return ONLY valid JSON in this format:

{{
    "intents": ["founder", "product"]
}}

Examples:

Question:
Who founded Apple?

Answer:
{{"intents": ["founder"]}}

Question:
Who runs Apple?

Answer:
{{"intents": ["ceo"]}}

Question:
What products does Apple make?

Answer:
{{"intents": ["product"]}}

Question:
What is the iPhone?

Answer:
{{"intents": ["general"]}}

Question:
Who founded Apple and what products does Apple produce?

Answer:
{{"intents": ["founder", "product"]}}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    text = response.content.strip()

    try:
        result = json.loads(text)

        return result["intents"]

    except Exception:

        return ["general"]