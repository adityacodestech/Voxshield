from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_student5.app.routes.health import router as health_router
from backend_student5.app.routes.analysis import router as analysis_router
from backend_student5.app.routes.audio import router as audio_router

app = FastAPI(
    title="AI Voice Security API",
    description="Backend for AI-powered real-time voice cloning detection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(audio_router)

@app.get("/")
def root():
    return {
        "message": "AI Voice Security API is running"
    }
