from fastapi import FastAPI
from pydantic import BaseModel
from hybrid_rag import hybrid_rag

app = FastAPI()


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Hybrid RAG API is running. Testing the FAST API server."}


@app.post("/chat")
def chat(request: ChatRequest):

    question = request.question

    # Later this will call your actual Hybrid RAG pipeline
    answer = hybrid_rag(question)

    return {
        "question": question,
        "answer": answer
    }