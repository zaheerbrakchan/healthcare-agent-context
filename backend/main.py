from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers import appointment_agent, preassessment_agent

app = FastAPI(title="Healthcare Context Agent System")

app.include_router(appointment_agent.router, prefix="/appointment", tags=["Appointment Agent"])
app.include_router(preassessment_agent.router, prefix="/preassessment", tags=["Preassessment Agent"])

@app.get("/")
def root():
    return {"message": "Healthcare Context Agent System Running!"}
