from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import call_llm
from services.vector_db import add_to_memory
from services.retrieval import intelligent_retrieval

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_with_preassessment_agent(req: ChatRequest):
    query_with_context = intelligent_retrieval(req.query)
    prompt = f"You are a hospital preassessment nurse. {query_with_context}"
    response = call_llm(prompt)
    add_to_memory(req.user_id, req.query + " " + response)
    return ChatResponse(response=response)
