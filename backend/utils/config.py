import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "500"))
FFMPEG_PRESET = os.getenv("FFMPEG_PRESET", "ultrafast")
FFMPEG_CRF = os.getenv("FFMPEG_CRF", "23")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "").strip()
SUPABASE_INPUT_PREFIX = os.getenv("SUPABASE_INPUT_PREFIX", "inputs").strip().strip("/")
SUPABASE_OUTPUT_PREFIX = os.getenv("SUPABASE_OUTPUT_PREFIX", "outputs").strip().strip("/")
SUPABASE_SIGNED_UPLOAD_EXPIRES_IN = int(
    os.getenv("SUPABASE_SIGNED_UPLOAD_EXPIRES_IN", "900")
)
SUPABASE_SIGNED_URL_EXPIRES_IN = int(
    os.getenv("SUPABASE_SIGNED_URL_EXPIRES_IN", "3600")
)
SUPABASE_DELETE_INPUTS = os.getenv("SUPABASE_DELETE_INPUTS", "true").lower() in {
    "1",
    "true",
    "yes",
}

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]


def ensure_directories():
    for folder in (UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR):
        folder.mkdir(parents=True, exist_ok=True)
