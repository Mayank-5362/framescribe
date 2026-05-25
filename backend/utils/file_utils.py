from pathlib import Path

from fastapi import HTTPException, UploadFile

from utils.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB


def validate_extension(filename: str):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )


async def save_upload_file(upload_file: UploadFile, destination: Path):
    size = 0
    chunk_size = 1024 * 1024
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024

    with destination.open("wb") as buffer:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise HTTPException(status_code=413, detail="File too large")
            buffer.write(chunk)

    await upload_file.close()
    return size
