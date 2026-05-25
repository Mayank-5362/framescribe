from pathlib import Path
from typing import Any

from supabase import create_client

from utils.config import (
    OUTPUT_DIR,
    SUPABASE_BUCKET,
    SUPABASE_INPUT_PREFIX,
    SUPABASE_OUTPUT_PREFIX,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_SIGNED_UPLOAD_EXPIRES_IN,
    SUPABASE_SIGNED_URL_EXPIRES_IN,
    SUPABASE_URL,
)

_CLIENT = None


def is_storage_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY and SUPABASE_BUCKET)


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        if not is_storage_configured():
            raise RuntimeError("Supabase storage is not configured.")
        _CLIENT = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _CLIENT


def _content_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".mp4":
        return "video/mp4"
    if suffix == ".vtt":
        return "text/vtt"
    if suffix == ".srt":
        return "text/plain"
    return "application/octet-stream"


def _normalize_prefix(prefix: str) -> str:
    cleaned = prefix.strip().strip("/")
    return cleaned


def _build_remote_path(filename: str, prefix: str) -> str:
    prefix = _normalize_prefix(prefix)
    return f"{prefix}/{filename}" if prefix else filename


def _get_error_message(response: Any) -> str | None:
    if response is None:
        return "Unexpected empty response"
    if isinstance(response, dict):
        error = response.get("error")
        if error:
            return str(error)
        return None
    error = getattr(response, "error", None)
    if error:
        return str(error)
    return None


def _create_signed_url(remote_path: str) -> str:
    storage = _get_client().storage.from_(SUPABASE_BUCKET)
    response = storage.create_signed_url(remote_path, SUPABASE_SIGNED_URL_EXPIRES_IN)
    if isinstance(response, dict):
        url = response.get("signedURL") or response.get("signedUrl") or response.get("signed_url")
        if url:
            return url
    raise RuntimeError("Failed to create a signed URL for the uploaded file.")


def create_upload_url(filename: str) -> dict:
    storage = _get_client().storage.from_(SUPABASE_BUCKET)
    remote_path = _build_remote_path(filename, SUPABASE_INPUT_PREFIX)
    response = storage.create_signed_upload_url(
        remote_path,
        SUPABASE_SIGNED_UPLOAD_EXPIRES_IN,
    )
    if isinstance(response, dict):
        url = response.get("signedURL") or response.get("signedUrl") or response.get("signed_url")
        path = response.get("path") or response.get("key") or remote_path
        if url:
            return {"upload_url": url, "storage_path": path}
    raise RuntimeError("Failed to create a signed upload URL.")


def upload_and_sign(local_path: Path) -> str:
    storage = _get_client().storage.from_(SUPABASE_BUCKET)
    remote_path = _build_remote_path(local_path.name, SUPABASE_OUTPUT_PREFIX)
    content_type = _content_type_for(local_path)

    with local_path.open("rb") as handle:
        response = storage.upload(
            remote_path,
            handle,
            file_options={"content-type": content_type, "upsert": True},
        )

    error_message = _get_error_message(response)
    if error_message:
        raise RuntimeError(f"Supabase upload failed: {error_message}")

    return _create_signed_url(remote_path)


def upload_outputs(result: dict) -> dict:
    output_path = OUTPUT_DIR / result["output_filename"]
    vtt_path = OUTPUT_DIR / result["vtt_filename"]
    srt_path = OUTPUT_DIR / result["srt_filename"]

    return {
        "output_url": upload_and_sign(output_path),
        "vtt_url": upload_and_sign(vtt_path),
        "srt_url": upload_and_sign(srt_path),
    }


def download_to_path(storage_path: str, local_path: Path):
    storage = _get_client().storage.from_(SUPABASE_BUCKET)
    response = storage.download(storage_path)

    data = None
    if isinstance(response, (bytes, bytearray)):
        data = response
    elif isinstance(response, dict):
        data = response.get("data")
    else:
        data = getattr(response, "data", None)

    if data is None:
        raise RuntimeError("Failed to download input from Supabase.")

    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(data)


def delete_remote(storage_path: str):
    storage = _get_client().storage.from_(SUPABASE_BUCKET)
    response = storage.remove([storage_path])
    error_message = _get_error_message(response)
    if error_message:
        raise RuntimeError(f"Supabase delete failed: {error_message}")
