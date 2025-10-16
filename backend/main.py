from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import appointment_agent_router, preassessment_agent_router
import os

load_dotenv()

app = FastAPI(title="Healthcare Context Agent System")

# Enable CORS (allow frontend JS to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your domain
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routers
app.include_router(appointment_agent_router.router, prefix="/appointment", tags=["appointment"])
app.include_router(preassessment_agent_router.router, prefix="/preassessment", tags=["preassessment"])

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Root route serves the main UI
@app.get("/")
def root():
    """
    Serves the frontend index.html when visiting "/"
    """
    return FileResponse(os.path.join("frontend", "index.html"))

# Optional health check
@app.get("/health")
def health():
    return {"status": "ok", "message": "Healthcare Agent API Running 🚀"}

