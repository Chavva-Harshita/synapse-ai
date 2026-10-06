FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/data/huggingface

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.13.0" \
    && python -m pip install -r requirements.txt

COPY app ./app

RUN groupadd --system --gid 10001 synapse \
    && useradd --system --uid 10001 --gid synapse --home-dir /home/synapse synapse \
    && mkdir -p /data/chroma /data/uploads /data/huggingface \
    && chown -R synapse:synapse /app /data

USER synapse

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
