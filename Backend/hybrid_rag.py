from vector_search import vector_search
from graph_search import graph_search
from llm_generate_ans import generate_answer
from query_router import classify_question


def hybrid_rag(question: str):

    # --------------------------------
    # 1. Identify all intents
    # --------------------------------

    intents = classify_question(question)

    print("\nQuestion:", question)
    print("Intents:", intents)


    # --------------------------------
    # 2. Initialize retrieval results
    # --------------------------------

    graph_results = []
    vector_results = []


    # --------------------------------
    # 3. Neo4j retrieval
    # --------------------------------

    if (
        "founder" in intents
        or "ceo" in intents
        or "product" in intents
    ):

        graph_results = graph_search(intents)


    # --------------------------------
    # 4. FAISS retrieval
    # --------------------------------

    vector_results = vector_search(
        question,
        top_k=3
    )


    # --------------------------------
    # 5. Convert FAISS Documents
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