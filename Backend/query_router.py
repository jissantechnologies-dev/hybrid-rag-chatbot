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
You are a query planner for a Hybrid RAG system.

Your job is to determine which retrieval methods are useful
for answering the user's question.

Available retrieval methods:

1. vector

Use vector retrieval for:
- factual information
- policies
- descriptions
- procedures
- documents
- manuals
- FAQs
- general knowledge contained in the document collection

2. graph

Use graph retrieval when the question requires:
- entities
- relationships
- connections
- ownership
- people
- organizations
- products
- structured relationships stored in Neo4j

3. both

Use both when the question requires information from
documents AND relationships/entities.

Return ONLY valid JSON.

Format:

{{
    "retrieval": "vector"
}}

or:

{{
    "retrieval": "graph"
}}

or:

{{
    "retrieval": "both"
}}

Examples:

Question:
How many casual leaves can employees carry forward?

Answer:
{{"retrieval": "vector"}}

Question:
What is the laptop reimbursement limit?

Answer:
{{"retrieval": "vector"}}

Question:
Who founded Apple?

Answer:
{{"retrieval": "both"}}

Question:
Who is the CEO of Apple?

Answer:
{{"retrieval": "both"}}

Question:
What products are connected to Apple?

Answer:
{{"retrieval": "graph"}}

Question:
Explain the company's travel reimbursement policy.

Answer:
{{"retrieval": "vector"}}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    text = response.content.strip()

    try:

        result = json.loads(text)

        retrieval = result.get(
            "retrieval",
            "vector"
        )

        if retrieval not in [
            "vector",
            "graph",
            "both"
        ]:
            return "vector"

        return retrieval

    except Exception:

        return "vector"