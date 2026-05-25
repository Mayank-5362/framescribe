from dataclasses import asdict, dataclass
from threading import Lock
from typing import Dict, Optional


@dataclass
class JobState:
    job_id: str
    status: str
    stage: str
    detail: str
    output_filename: Optional[str] = None
    vtt_filename: Optional[str] = None
    srt_filename: Optional[str] = None
    output_url: Optional[str] = None
    vtt_url: Optional[str] = None
    srt_url: Optional[str] = None


_jobs: Dict[str, JobState] = {}
_lock = Lock()


def create_job(job_id: str) -> dict:
    job = JobState(
        job_id=job_id,
        status="queued",
        stage="queued",
        detail="Queued",
    )
    with _lock:
        _jobs[job_id] = job
    return asdict(job)


def update_job(job_id: str, **updates) -> Optional[dict]:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return None
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        return asdict(job)


def get_job(job_id: str) -> Optional[dict]:
    with _lock:
        job = _jobs.get(job_id)
        return asdict(job) if job else None
