from fastapi import FastAPI

from backend_student5.app.routes.health import router as health_router
from backend_student5.app.routes.analysis import router as analysis_router

app = FastAPI(
    title="AI Voice Security API",
    description="Backend for AI-powered real-time voice cloning detection",
    version="1.0.0",
)

app.include_router(
    health_router,
    prefix="/api/v1"
)

app.include_router(
    analysis_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "message": "AI Voice Security API is running"
    }