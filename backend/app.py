import os
import shutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.video import router as video_router
from utils.config import (
    CORS_ORIGINS,
    SUPABASE_BUCKET,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
    ensure_directories,
)

app = FastAPI(title="AI Video Subtitle Generator", version="1.0.0")

# Create storage folders on startup
ensure_directories()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

app.include_router(video_router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "FrameScribe backend is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/deploy-check")
async def deploy_check():
    whisper_bin = os.getenv("WHISPER_CPP_BIN")
    whisper_model = os.getenv("WHISPER_CPP_MODEL")
    ffmpeg_path = shutil.which("ffmpeg")

    missing_required = []
    if not whisper_bin:
        missing_required.append("WHISPER_CPP_BIN")
    if not whisper_model:
        missing_required.append("WHISPER_CPP_MODEL")
    if not ffmpeg_path:
        missing_required.append("FFMPEG")

    supabase_missing = []
    if not SUPABASE_URL:
        supabase_missing.append("SUPABASE_URL")
    if not SUPABASE_SERVICE_ROLE_KEY:
        supabase_missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if not SUPABASE_BUCKET:
        supabase_missing.append("SUPABASE_BUCKET")

    def _exists(path_value: str | None) -> bool:
        if not path_value:
            return False
        return Path(path_value).exists()

    return {
        "status": "ok" if not missing_required else "error",
        "required_missing": missing_required,
        "ffmpeg_found": bool(ffmpeg_path),
        "whisper_cpp_bin_set": bool(whisper_bin),
        "whisper_cpp_bin_exists": _exists(whisper_bin),
        "whisper_cpp_model_set": bool(whisper_model),
        "whisper_cpp_model_exists": _exists(whisper_model),
        "supabase_configured": not supabase_missing,
        "supabase_missing": supabase_missing,
        "cors_origins": CORS_ORIGINS,
    }
