from Backend.graph_search import graph_search


questions = [
    "Who is the CEO of Apple?",
    "Who founded Apple?",
    "What products does Apple produce?",
    "What is the iPhone?"
]


for question in questions:

    print("\n==============================")
    print("Question:", question)
    print("==============================")

    results = graph_search(question)

    for result in results:
        print(result)