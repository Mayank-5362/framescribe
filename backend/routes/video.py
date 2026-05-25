from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.job_queue import enqueue_job
from services.job_store import create_job, get_job, update_job
from services.storage_service import create_upload_url, is_storage_configured
from utils.config import OUTPUT_DIR, UPLOAD_DIR
from utils.file_utils import save_upload_file, validate_extension

router = APIRouter()


class UploadUrlRequest(BaseModel):
    filename: str


class ProcessRequest(BaseModel):
    job_id: str
    storage_path: str


@router.post("/upload-url")
async def upload_url(payload: UploadUrlRequest):
    if not is_storage_configured():
        raise HTTPException(
            status_code=400,
            detail="Supabase storage is not configured",
        )

    filename = payload.filename.strip() if payload.filename else ""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    validate_extension(filename)

    job_id = uuid4().hex
    ext = Path(filename).suffix.lower()
    storage_filename = f"{job_id}{ext}"

    create_job(job_id)
    update_job(
        job_id,
        status="processing",
        stage="uploading_input",
        detail="Awaiting upload",
    )

    try:
        signed = create_upload_url(storage_filename)
    except Exception as exc:
        update_job(job_id, status="error", stage="error", detail=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "job_id": job_id,
        "upload_url": signed["upload_url"],
        "storage_path": signed["storage_path"],
    }


@router.post("/process")
async def process_upload(payload: ProcessRequest):
    if not payload.job_id:
        raise HTTPException(status_code=400, detail="job_id is required")
    if not payload.storage_path:
        raise HTTPException(status_code=400, detail="storage_path is required")

    if not get_job(payload.job_id):
        create_job(payload.job_id)

    update_job(
        payload.job_id,
        status="queued",
        stage="queued",
        detail="Queued",
    )
    enqueue_job(payload.job_id, storage_path=payload.storage_path)

    return {
        "job_id": payload.job_id,
        "status": "queued",
    }


@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    validate_extension(file.filename)

    job_id = uuid4().hex
    ext = Path(file.filename).suffix.lower()
    input_path = UPLOAD_DIR / f"{job_id}{ext}"

    create_job(job_id)

    try:
        await save_upload_file(file, input_path)
        enqueue_job(job_id, input_path)
    except HTTPException as exc:
        update_job(job_id, status="error", stage="error", detail=str(exc.detail))
        if input_path.exists():
            input_path.unlink()
        raise
    except Exception as exc:
        update_job(job_id, status="error", stage="error", detail=str(exc))
        if input_path.exists():
            input_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")

    return {
        "job_id": job_id,
        "status": "queued",
    }


@router.get("/progress/{job_id}")
async def progress(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/download/{filename}")
async def download_file(filename: str):
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "application/octet-stream"
    suffix = file_path.suffix.lower()
    if suffix == ".mp4":
        media_type = "video/mp4"
    elif suffix == ".vtt":
        media_type = "text/vtt"
    elif suffix == ".srt":
        media_type = "text/plain"

    return FileResponse(path=file_path, filename=safe_name, media_type=media_type)
