# FrameScribe (Whisper + FastAPI + React)

FrameScribe is a beginner-friendly, production-style web app that converts videos into subtitled videos using whisper.cpp and FFmpeg. This project is optimized for low-end laptops by using the Whisper tiny/base models, streaming uploads, and avoiding memory-heavy operations.

## Features
- Upload a video and generate English subtitles automatically
- Extract audio, transcribe with Whisper, and burn subtitles into the video
- Preview and download the processed video
- Optional Supabase Storage integration for outputs
- FastAPI backend with clean, modular services
- React + Vite + Tailwind frontend with a modern glass UI
- Docker support and deployment guides (Render + Vercel)

## Tech Stack
- Frontend: React, Vite, Tailwind CSS
- Backend: FastAPI (Python)
- AI Model: whisper.cpp (tiny/base)
- Video Processing: FFmpeg

## Project Structure
```
project/
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── App.jsx
│   ├── main.jsx
│   └── package.json
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── uploads/
│   ├── outputs/
│   ├── temp/
│   ├── requirements.txt
│   └── whisper_service.py
├── README.md
├── .gitignore
└── docker-compose.yml
```

## Requirements
- Python 3.10+ and pip
- Node.js 18+ and npm
- FFmpeg installed and available in PATH

## Environment Setup Guide
1. Install FFmpeg
   - Windows (Chocolatey): `choco install ffmpeg`
   - macOS (Homebrew): `brew install ffmpeg`
   - Ubuntu: `sudo apt-get update && sudo apt-get install ffmpeg`

2. Create Python environment
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install frontend dependencies
   4. Install whisper.cpp
      - Download a prebuilt binary from https://github.com/ggerganov/whisper.cpp/releases
      - Download a ggml model from https://huggingface.co/ggerganov/whisper.cpp
      - Example low RAM model: `ggml-tiny.en.bin`
      - Set the environment variables below so the backend can find the binary and model.
   ```bash
   cd frontend
   npm install
   ```

## Local Development Commands
- Backend (FastAPI)
  ```bash
  cd backend
  uvicorn app:app --reload --port 8000
  ```

- Frontend (Vite)
  ```bash
  cd frontend
  npm run dev
  ```

The frontend runs at `http://localhost:5173` and calls the backend at `http://localhost:8000`.

## VS Code Setup Instructions
- Recommended extensions:
  - Python
  - Pylance
  - ESLint
  - Tailwind CSS IntelliSense
- Use the built-in terminal to run the backend and frontend in separate terminals.

## Backend Environment Variables
You can set these in your shell or in a `.env` file:
- `WHISPER_MODEL` (default: `tiny`) — use `tiny` or `base` for low RAM
- `WHISPER_CPP_BIN` — path to `whisper-cli.exe` (or `main.exe`)
- `WHISPER_CPP_MODEL` — path to `ggml-*.bin` model file
- `WHISPER_CPP_THREADS` (default: `2`) — reduce CPU load on low-end machines
- `MAX_UPLOAD_MB` (default: `500`) — upload limit
- `CORS_ORIGINS` (default: `http://localhost:5173`)
- `FFMPEG_PRESET` (default: `ultrafast`) — faster burn-in at lower quality
- `FFMPEG_CRF` (default: `23`) — lower is higher quality (slower)

### Optional: Supabase Storage (Pattern 1)
If you want Render to process locally and store outputs in Supabase Storage, set:
- `SUPABASE_URL` — your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` — service role key (server-side only)
- `SUPABASE_BUCKET` — storage bucket name
- `SUPABASE_OUTPUT_PREFIX` (default: `outputs`) — folder prefix in the bucket
- `SUPABASE_SIGNED_URL_EXPIRES_IN` (default: `3600`) — signed URL TTL in seconds
- `SUPABASE_INPUT_PREFIX` (default: `inputs`) — folder prefix for input uploads
- `SUPABASE_SIGNED_UPLOAD_EXPIRES_IN` (default: `900`) — signed upload URL TTL
- `SUPABASE_DELETE_INPUTS` (default: `true`) — delete uploaded inputs after processing

When configured, the backend uploads MP4/SRT/VTT outputs to Supabase and returns
signed URLs to the frontend. Local output files are deleted after upload.

### Supabase Storage (Pattern 2 - Recommended)
Best overall: Direct upload to Supabase, then the backend downloads and processes.

Why it is best:
- Avoids backend upload timeouts on Render (large files)
- Reduces backend bandwidth and keeps Render free tier happier
- Lets you use signed URLs and auto-expire files cleanly

Flow summary:
1) Frontend requests `POST /upload-url` with the filename.
2) Frontend uploads the file directly to Supabase via the signed URL.
3) Frontend calls `POST /process` with `job_id` and `storage_path`.

This flow avoids large uploads to Render and is recommended for deployment.

## Deployment Guide
### Render (Backend)
Use the included Dockerfile and render.yaml for a one-click setup.

1. Create a new Render Web Service (Docker).
2. Point it at this repo root.
3. Render will detect [render.yaml](render.yaml) and build using [backend/Dockerfile](backend/Dockerfile).
4. Set these env vars in Render:
   - `CORS_ORIGINS` = your Vercel domain
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_BUCKET`

Docker build args (optional):
- `WHISPER_CPP_VERSION` (default `1.7.1`)
- `WHISPER_CPP_ARCHIVE` (default `whisper.cpp-${WHISPER_CPP_VERSION}-linux-x64.tar.gz`)
- `WHISPER_CPP_MODEL_URL` (default `ggml-base.en.bin`)

### Vercel (Frontend)
1. Create a new Vercel project.
2. Set the root directory to `frontend`.
3. Set build command to `npm run build`.
4. Set output directory to `dist`.
5. Add `VITE_API_BASE_URL` as the Render backend URL.

### Supabase (Storage)
1. Create a bucket (private is recommended).
2. Add the Supabase env vars on Render.
3. The app will upload inputs and outputs and return signed URLs.

## Docker Support
Build and run both services:
```bash
docker-compose up --build
```

Frontend: `http://localhost:5173`
Backend: `http://localhost:8000`

## Low-End Optimization Tips
- Use `WHISPER_MODEL=tiny` or `base` only.
- Prefer `whisper.cpp` on older CPUs.
- Avoid large video files (short clips process faster).
- Keep other applications closed while processing.

## API Endpoints
- `POST /upload` — upload a video and start queued processing
- `POST /upload-url` — create signed upload URL for Supabase (Pattern 2)
- `POST /process` — start processing for a Supabase upload (Pattern 2)
- `GET /progress/{job_id}` — check processing status and get output filenames
- `GET /download/{filename}` — download output files
- `GET /health` — health check

## Troubleshooting
- If FFmpeg is missing, install it and restart your terminal.
- If the model downloads are slow, try a smaller model (`tiny`).
- Large videos may take several minutes on low-end hardware.
