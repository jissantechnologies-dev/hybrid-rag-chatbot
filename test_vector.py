from Backend.vector_search import vector_search


question = "Who founded Apple?"


results = vector_search(question, top_k=2)


print("\nQuestion:")
print(question)

print("\nRetrieved Documents:")
print("====================")


for i, document in enumerate(results, start=1):

    print(f"\n--- Result {i} ---")

    print(document.page_content)

    print("\nMetadata:")
    print(document.metadata)