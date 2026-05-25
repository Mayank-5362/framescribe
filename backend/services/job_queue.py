import queue
import threading
from pathlib import Path

from services.job_store import update_job
from services.storage_service import (
    delete_remote,
    download_to_path,
    is_storage_configured,
    upload_outputs,
)
from services.video_service import process_video
from utils.config import OUTPUT_DIR, SUPABASE_DELETE_INPUTS, UPLOAD_DIR


_job_queue: "queue.Queue[tuple[str, Path | None, str | None]]" = queue.Queue()


def _safe_unlink(path: Path):
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def _cleanup_outputs(result: dict):
    for key in ("output_filename", "vtt_filename", "srt_filename"):
        filename = result.get(key)
        if filename:
            _safe_unlink(OUTPUT_DIR / filename)


def enqueue_job(
    job_id: str,
    input_path: Path | None = None,
    storage_path: str | None = None,
):
    if not input_path and not storage_path:
        raise ValueError("input_path or storage_path is required")
    _job_queue.put((job_id, input_path, storage_path))


def _local_input_path(job_id: str, storage_path: str) -> Path:
    suffix = Path(storage_path).suffix or ".mp4"
    return UPLOAD_DIR / f"{job_id}{suffix}"


def _worker():
    while True:
        job_id, input_path, storage_path = _job_queue.get()
        local_input = input_path
        try:
            update_job(
                job_id,
                status="processing",
                stage="extracting_audio",
                detail="Starting processing",
            )

            if storage_path:
                update_job(
                    job_id,
                    status="processing",
                    stage="downloading_input",
                    detail="Downloading upload",
                )
                local_input = _local_input_path(job_id, storage_path)
                download_to_path(storage_path, local_input)

            def progress(stage: str, detail: str):
                update_job(job_id, status="processing", stage=stage, detail=detail)

            if local_input is None:
                raise RuntimeError("Missing input file for processing")

            result = process_video(local_input, progress_cb=progress)
            output_payload = {}

            if is_storage_configured():
                update_job(
                    job_id,
                    status="processing",
                    stage="uploading_outputs",
                    detail="Uploading outputs",
                )
                output_payload = upload_outputs(result)
                _cleanup_outputs(result)
            update_job(
                job_id,
                status="done",
                stage="done",
                detail="Completed",
                **result,
                **output_payload,
            )
            if storage_path and SUPABASE_DELETE_INPUTS:
                try:
                    delete_remote(storage_path)
                except Exception:
                    pass
        except Exception as exc:
            update_job(job_id, status="error", stage="error", detail=str(exc))
        finally:
            if local_input is not None:
                _safe_unlink(local_input)
            _job_queue.task_done()


_worker_thread = threading.Thread(target=_worker, daemon=True)
_worker_thread.start()
