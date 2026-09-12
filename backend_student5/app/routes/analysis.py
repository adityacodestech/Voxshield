from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from inference.detector import detect_voice
from risk_engine import get_risk_result
from backend_student5.app.services.blockchain_audit import record_risk_score
from backend_student5.app.schemas.analysis import AnalysisResponse

router = APIRouter()

# Always store uploads inside Student 5's backend folder
BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):

    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    file_extension = Path(file.filename).suffix.lower()

    # Validate audio format
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {file_extension}"
        )

    analysis_id = str(uuid.uuid4())
    saved_filename = f"{analysis_id}{file_extension}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        # Save uploaded audio
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty"
            )

        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # Send audio to Student 1 detector
        detection_result = detect_voice(str(file_path))

        risk_result = get_risk_result(
            ai_probability=float(detection_result["ai_probability"]),
            speaker_mismatch=0.0,
            caller_risk=0.0,
            transaction_risk=0.0,
            behavioral_risk=0.0,
        )

        audit_result = record_risk_score(int(risk_result["risk_score"]))

        return {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "status": "analyzed",
            "detection": detection_result,
            "risk": risk_result,
            "audit": audit_result
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Audio analysis failed: {str(exc)}"
        )

    finally:
        # Remove temporary uploaded audio after analysis
        if file_path.exists():
            file_path.unlink()