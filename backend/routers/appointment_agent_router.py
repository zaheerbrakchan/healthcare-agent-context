import logging
from fastapi import APIRouter, Body
from pydantic import BaseModel
from agents.appointment_agent.agent import AppointmentAgent

logger = logging.getLogger("appointment_agent")
logging.basicConfig(level=logging.INFO)

router = APIRouter()
agent = AppointmentAgent()

class AppointmentRequest(BaseModel):
    text: str
    phone: str = None

@router.post("/chat")
def chat(request: AppointmentRequest = Body(...)):
    logger.info(f"Received query: {request.text}")
    print(f"Received query: {request.text}", flush=True)
    response = agent.handle_query(user_query=request.text, patient_phone=request.phone)
    logger.info(f"Agent response: {response}")
    # ✅ Extract only the plain text reply
    reply_text = response.get("reply") if isinstance(response, dict) else str(response)

    logger.info(f"Agent reply: {reply_text}")
    return reply_text
