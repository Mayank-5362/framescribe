from pathlib import Path
from uuid import uuid4

from services.whisper_service import transcribe_audio
from utils.config import OUTPUT_DIR, TEMP_DIR, ensure_directories
from utils.ffmpeg_utils import burn_subtitles, convert_video_to_audio

def _notify(progress_cb, stage: str, detail: str):
    if progress_cb:
        progress_cb(stage, detail)


def process_video(input_path: Path, progress_cb=None) -> dict:
    ensure_directories()

    base = f"{input_path.stem}-{uuid4().hex[:8]}"
    audio_path = TEMP_DIR / f"{base}.wav"

    try:
        _notify(progress_cb, "extracting_audio", "Extracting audio")
        convert_video_to_audio(input_path, audio_path)

        _notify(progress_cb, "transcribing", "Transcribing with whisper.cpp")
        output_base = OUTPUT_DIR / base
        vtt_path, srt_path = transcribe_audio(str(audio_path), output_base)

        output_video = OUTPUT_DIR / f"{base}_subtitled.mp4"
        _notify(progress_cb, "burning_subtitles", "Burning subtitles into video")
        burn_subtitles(input_path, srt_path, output_video)

        return {
            "output_filename": output_video.name,
            "vtt_filename": vtt_path.name,
            "srt_filename": srt_path.name,
        }
    finally:
        if audio_path.exists():
            audio_path.unlink()
