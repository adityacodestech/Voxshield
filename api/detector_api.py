"""
api/detector_api.py — VoxShield FastAPI Endpoint
=================================================
REST API that wraps the detect_voice() inference function.

Endpoints:
    GET  /health        → service health check
    GET  /model-info    → current model metadata
    POST /detect-voice  → detect AI voice from uploaded audio file

Start the server:
    uvicorn api.detector_api:app --host 0.0.0.0 --port 8000 --reload

Or:
    python api/detector_api.py

Integration:
    Student 2 → POST /detect-voice with speech segment WAV
    Student 5 → receives JSON with ai_probability

    API contract (POST /detect-voice response):
    {
      "prediction": "AI_GENERATED",
      "ai_probability": 0.94,
      "genuine_probability": 0.06,
      "threshold": 0.60,
      "model_version": "voxshield-v1"
    }
"""

import sys
import tempfile
import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg
from inference.detector import detect_voice


# ─────────────────────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="VoxShield — AI Voice Detector",
    description=(
        "Real-time AI/synthetic voice detection module for VoxShield. "
        "Upload a speech audio segment and receive AI vs genuine probabilities."
    ),
    version="1.0.0",
    docs_url="/docs",    # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",
)

# Allow cross-origin requests from the VoxShield frontend and other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    model: str
    version: str
    sample_rate: int
    segment_duration: float
    n_mels: int
    threshold: float

class DetectionResponse(BaseModel):
    prediction: str          # "REAL" | "AI_GENERATED"
    ai_probability: float    # [0, 1] — use this in the Risk Engine
    genuine_probability: float
    threshold: float
    model_version: str


# ─────────────────────────────────────────────────────────────────────────────
# Model state tracking
# ─────────────────────────────────────────────────────────────────────────────

_model_ready = False


@app.on_event("startup")
async def startup_event():
    """Pre-load the model when the server starts."""
    global _model_ready
    try:
        # Trigger lazy-load by calling detect_voice on a silent dummy file
        # (the model loads itself on first call)
        print("[VoxShield API] Pre-loading model …")
        from inference.detector import _load_model
        _load_model()
        _model_ready = True
        print("[VoxShield API] Model ready. Server started.")
    except FileNotFoundError:
        print("[VoxShield API] ⚠  No checkpoint found. "
              "Train the model first, then restart the server.")
        _model_ready = False


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """
    Service health check.

    Returns 200 if the server is running.
    model_loaded = false means the model file was not found at startup —
    the server is running but cannot detect voices yet.
    """
    return {"status": "ok", "model_loaded": _model_ready}


@app.get("/model-info", response_model=ModelInfoResponse, tags=["System"])
async def model_info():
    """
    Return current model metadata.

    Student 2 / Student 5 can call this to verify they are sending audio
    in the correct format.
    """
    from inference.detector import _threshold
    return {
        "model": "VoxShield Voice Detector",
        "version": cfg.MODEL_VERSION,
        "sample_rate": cfg.SAMPLE_RATE,
        "segment_duration": cfg.SEGMENT_DURATION,
        "n_mels": cfg.N_MELS,
        "threshold": _threshold,
    }


@app.post(
    "/detect-voice",
    response_model=DetectionResponse,
    tags=["Detection"],
    summary="Detect AI-generated voice",
    description=(
        "Upload a speech audio segment (.wav, .flac, .mp3) and receive "
        "AI vs genuine probability scores. "
        "**Always use ai_probability in the Risk Engine, not just the prediction label.**"
    ),
)
async def detect_voice_endpoint(
    file: UploadFile = File(..., description="Speech audio file (.wav recommended)")
):
    """
    Main detection endpoint.

    - Accepts: multipart/form-data with an audio file
    - Returns: DetectionResponse JSON

    Integration notes:
        - Student 2 sends a speech segment after VAD/segmentation
        - Student 5 uses ai_probability (not just prediction) in the Risk Engine
        - Frontend can display both prediction label and probability bar
    """
    if not _model_ready:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Train the model and restart the server."
        )

    # Validate file type
    allowed_suffixes = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}
    suffix = Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in allowed_suffixes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. "
                   f"Allowed: {', '.join(allowed_suffixes)}"
        )

    # Save uploaded file to a temp location, run detection, clean up
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, dir=tempfile.gettempdir()
        ) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        result = detect_voice(tmp_path)
        return JSONResponse(content=result)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=f"Audio processing failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


# ─────────────────────────────────────────────────────────────────────────────
# Run directly
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting VoxShield API server …")
    print(f"  Swagger UI : http://{cfg.API_HOST}:{cfg.API_PORT}/docs")
    print(f"  Health     : http://{cfg.API_HOST}:{cfg.API_PORT}/health")
    print(f"  Detect     : POST http://{cfg.API_HOST}:{cfg.API_PORT}/detect-voice")
    uvicorn.run(
        "api.detector_api:app",
        host=cfg.API_HOST,
        port=cfg.API_PORT,
        reload=False,   # set True during development only
    )
