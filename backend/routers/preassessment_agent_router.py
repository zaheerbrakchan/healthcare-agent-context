import logging
from fastapi import APIRouter, Body
from pydantic import BaseModel
from agents.preassessment_agent.agent import PreassessmentAgent

logger = logging.getLogger("preassessment_agent")
logging.basicConfig(level=logging.INFO)

router = APIRouter()
agent = PreassessmentAgent()


class PreassessmentRequest(BaseModel):
    text: str
    phone: str = None  # optional, agent can ask if not provided


@router.post("/chat")
def chat(request: PreassessmentRequest = Body(...)):
    logger.info(f"Received query: {request.text}")
    print(f"Received query: {request.text}", flush=True)

    # Handle the query through the preassessment agent
    response = agent.handle_query(user_query=request.text, patient_phone=request.phone)

    logger.info(f"Agent response: {response}")
    # If response is dict, extract 'reply'; else, return as string
    reply_text = response.get("reply") if isinstance(response, dict) else str(response)

    logger.info(f"Agent reply: {reply_text}")
    return reply_text
