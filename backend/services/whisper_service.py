import os
import shutil
import subprocess
from pathlib import Path


def _get_whisper_cpp_bin() -> str:
    configured = os.getenv("WHISPER_CPP_BIN")
    if configured:
        path = Path(configured)
        if path.exists():
            return str(path)

    for name in ("whisper-cli", "whisper-cli.exe", "whisper", "whisper.exe", "main", "main.exe"):
        found = shutil.which(name)
        if found:
            return found

    raise RuntimeError(
        "whisper.cpp binary not found. Set WHISPER_CPP_BIN or add whisper-cli to PATH."
    )


def _get_model_path() -> str:
    model_path = os.getenv("WHISPER_CPP_MODEL")
    if not model_path:
        raise RuntimeError(
            "WHISPER_CPP_MODEL is not set. Download a ggml model and set its path."
        )

    path = Path(model_path)
    if not path.exists():
        raise RuntimeError(f"WHISPER_CPP_MODEL does not exist: {path}")

    return str(path)


def _transcribe_with_whisper_cpp(audio_path: str, output_base: Path):
    whisper_bin = _get_whisper_cpp_bin()
    model_path = _get_model_path()
    threads = os.getenv("WHISPER_CPP_THREADS", "2")

    args = [
        whisper_bin,
        "-m",
        model_path,
        "-f",
        audio_path,
        "-l",
        "en",
        "--threads",
        threads,
        "-of",
        str(output_base),
        "-osrt",
        "-ovtt",
        "--beam-size",
        "1",
        "--best-of",
        "1",
        "--temperature",
        "0.0",
    ]

    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "whisper.cpp failed"
        raise RuntimeError(message)

    return output_base.with_suffix(".vtt"), output_base.with_suffix(".srt")


def transcribe_audio(audio_path: str, output_base: Path):
    return _transcribe_with_whisper_cpp(audio_path, output_base)
