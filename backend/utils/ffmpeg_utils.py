import shutil
import subprocess
from pathlib import Path
from utils.config import FFMPEG_CRF, FFMPEG_PRESET


class FFmpegError(RuntimeError):
    pass


def ensure_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise FFmpegError("FFmpeg not found in PATH. Please install ffmpeg.")


def run_ffmpeg(args: list[str]):
    ensure_ffmpeg()
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "FFmpeg failed"
        raise FFmpegError(message)


def to_ffmpeg_filter_path(path: Path) -> str:
    normalized = str(path).replace("\\", "/")
    normalized = normalized.replace(":", "\\:")
    normalized = normalized.replace("'", "\\'")
    return normalized


def convert_video_to_audio(video_path: Path, audio_path: Path):
    args = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        "-loglevel",
        "error",
        str(audio_path),
    ]
    run_ffmpeg(args)


def burn_subtitles(video_path: Path, subtitle_path: Path, output_path: Path):
    subtitle_filter_path = to_ffmpeg_filter_path(subtitle_path)
    subtitle_filter = f"subtitles=filename='{subtitle_filter_path}'"

    args = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        subtitle_filter,
        "-c:v",
        "libx264",
        "-preset",
        FFMPEG_PRESET,
        "-crf",
        str(FFMPEG_CRF),
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-loglevel",
        "error",
        str(output_path),
    ]
    run_ffmpeg(args)
