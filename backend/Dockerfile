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
		git \
		build-essential \
		cmake \
	&& rm -rf /var/lib/apt/lists/*

ARG WHISPER_CPP_VERSION=v1.8.4
ARG WHISPER_CPP_MODEL_URL=https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

RUN git clone --depth 1 --branch ${WHISPER_CPP_VERSION} https://github.com/ggml-org/whisper.cpp.git /tmp/whisper.cpp \
	&& cmake -S /tmp/whisper.cpp -B /tmp/whisper.cpp/build -DCMAKE_BUILD_TYPE=Release \
	&& cmake --build /tmp/whisper.cpp/build --config Release -j 2 \
	&& mkdir -p /opt/whisper \
	&& cp /tmp/whisper.cpp/build/bin/whisper-cli /opt/whisper/whisper-cli \
	&& sh -c 'set -e; \
		whisper_lib=$(find /tmp/whisper.cpp/build -name "libwhisper*.so*" -type f -print -quit); \
		ggml_lib=$(find /tmp/whisper.cpp/build -name "libggml*.so*" -type f -print -quit); \
		if [ -z "$whisper_lib" ]; then echo "libwhisper shared library not found"; exit 1; fi; \
		if [ -z "$ggml_lib" ]; then echo "libggml shared library not found"; exit 1; fi; \
		find /tmp/whisper.cpp/build -name "libwhisper*.so*" -type f -exec cp {} /usr/local/lib/ \;; \
		find /tmp/whisper.cpp/build -name "libggml*.so*" -type f -exec cp {} /usr/local/lib/ \;;' \
	&& ldconfig \
	&& rm -rf /tmp/whisper.cpp

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
