from typing import Optional, List
from pydantic import BaseModel


class DetectionResult(BaseModel):
    prediction: str
    ai_probability: float
    genuine_probability: float
    threshold: float
    model_version: str


class RiskResult(BaseModel):
    risk_score: Optional[int] = None
    severity: str
    action: str
    reasons: List[str]


class AnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    content_type: Optional[str] = None
    status: str
    detection: DetectionResult
    risk: Optional[RiskResult] = None
    audit: Optional[dict] = None