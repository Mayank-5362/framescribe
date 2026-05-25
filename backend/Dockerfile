FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ffmpeg \
		wget \
		ca-certificates \
		libgomp1 \
	&& rm -rf /var/lib/apt/lists/*

ARG WHISPER_CPP_VERSION=1.7.1
ARG WHISPER_CPP_ARCHIVE=whisper.cpp-${WHISPER_CPP_VERSION}-linux-x64.tar.gz
ARG WHISPER_CPP_MODEL_URL=https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

RUN mkdir -p /opt/whisper \
	&& wget -qO /tmp/whisper.tar.gz \
		https://github.com/ggerganov/whisper.cpp/releases/download/v${WHISPER_CPP_VERSION}/${WHISPER_CPP_ARCHIVE} \
	&& tar -xzf /tmp/whisper.tar.gz -C /opt/whisper --strip-components=1 \
	&& rm /tmp/whisper.tar.gz

RUN mkdir -p /opt/models \
	&& wget -qO /opt/models/ggml-base.en.bin ${WHISPER_CPP_MODEL_URL}

ENV WHISPER_CPP_BIN=/opt/whisper/whisper-cli \
	WHISPER_CPP_MODEL=/opt/models/ggml-base.en.bin \
	WHISPER_CPP_THREADS=2 \
	FFMPEG_PRESET=ultrafast \
	FFMPEG_CRF=23

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
