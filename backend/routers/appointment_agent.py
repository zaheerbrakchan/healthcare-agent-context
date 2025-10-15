from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import call_llm
from services.vector_db import add_to_memory
from services.retrieval import intelligent_retrieval

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import SessionLocal
from models.schemas import ResourceCalendar
from datetime import datetime, date

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=ChatResponse)
def chat_with_appointment_agent(req: ChatRequest):
    query_with_context = intelligent_retrieval(req.query)
    prompt = f"You are a hospital appointment booking assistant. {query_with_context}"
    response = call_llm(prompt)
    add_to_memory(req.user_id, req.query + " " + response)
    return ChatResponse(response=response)


@router.get("/slots")
def get_slots(
    doctor_id: int | None = None,
    department: str | None = None,
    date_filter: str | None = None,  # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    query = db.query(ResourceCalendar).filter(ResourceCalendar.status == "Available")

    if doctor_id:
        query = query.filter(ResourceCalendar.resource_id == doctor_id)
    if department:
        query = query.filter(ResourceCalendar.department.ilike(f"%{department}%"))
    if date_filter:
        # Filter by start_datetime date
        query = query.filter(ResourceCalendar.start_datetime >= f"{date_filter} 00:00:00",
                             ResourceCalendar.start_datetime <= f"{date_filter} 23:59:59")

    results = query.all()
    return [{"slot_id": r.slot_id,
             "resource_id": r.resource_id,
             "department": r.department,
             "start_datetime": r.start_datetime,
             "end_datetime": r.end_datetime,
             "status": r.status} for r in results]

