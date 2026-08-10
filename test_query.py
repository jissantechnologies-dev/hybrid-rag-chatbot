from Backend.query_router import classify_question


questions = [
    "Who founded Apple?",
    "Who runs Apple?",
    "What products does Apple make?",
    "What is the iPhone?",
    "Who founded Apple and what products does Apple produce?"
]


for question in questions:

    intents = classify_question(question)

    print("\nQuestion:", question)
    print("Intents:", intents)