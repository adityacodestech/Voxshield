from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):

    analysis_id = str(uuid.uuid4())

    file_extension = Path(file.filename).suffix
    saved_filename = f"{analysis_id}{file_extension}"

    file_path = UPLOAD_DIR / saved_filename

    contents = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    return {
        "analysis_id": analysis_id,
        "filename": file.filename,
        "saved_file": str(file_path),
        "content_type": file.content_type,
        "status": "received"
    }