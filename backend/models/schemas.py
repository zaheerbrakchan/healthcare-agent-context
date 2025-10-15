from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from db import Base

class ChatRequest(BaseModel):
    user_id: str
    query: str

class ChatResponse(BaseModel):
    response: str


class ResourceCalendar(Base):
    __tablename__ = "resource_calendar"

    slot_id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("doctors.id"))
    department = Column(String)
    start_datetime = Column(TIMESTAMP)
    end_datetime = Column(TIMESTAMP)
    status = Column(String)
