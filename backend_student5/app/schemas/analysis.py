from pydantic import BaseModel
from typing import Optional


class DetectionResult(BaseModel):
    prediction: str
    ai_probability: float
    genuine_probability: float
    threshold: float
    model_version: str


class AnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    content_type: Optional[str] = None
    status: str
    detection: DetectionResult
    risk: Optional[dict] = None
    audit: Optional[dict] = None