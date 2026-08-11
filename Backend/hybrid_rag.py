from .vector_search import vector_search
from .graph_search import graph_search
from .llm_generate_ans import generate_answer
from .query_router import classify_question


def hybrid_rag(question: str):

    # --------------------------------
    # 1. Determine retrieval strategy
    # --------------------------------

    retrieval = classify_question(question)

    print("\nQuestion:", question)
    print("Retrieval strategy:", retrieval)

    # --------------------------------
    # 2. Initialize results
    # --------------------------------

    graph_results = []
    vector_results = []

    # --------------------------------
    # 3. Vector retrieval
    # --------------------------------

    if retrieval in ["vector", "both"]:
        vector_results = vector_search(
            question,
            top_k=3
        )

    # --------------------------------
    # 4. Graph retrieval
    # --------------------------------

    if retrieval in ["graph", "both"]:
        graph_results = graph_search(question)

    # --------------------------------
    # 5. Convert FAISS results
    # --------------------------------

    vector_context = []

    for document in vector_results:
        vector_context.append({
            "content": document.page_content,
            "metadata": document.metadata
        })

    # --------------------------------
    # 6. Combine context
    # --------------------------------

    context = {
        "graph_context": graph_results,
        "vector_context": vector_context
    }

    # --------------------------------
    # 7. Generate answer
    # --------------------------------

    answer = generate_answer(
        question,
        context
    )

    return answer