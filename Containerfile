# Image for the Cities API demo: a single-stage Python 3.14 slim image that
# installs the pinned dependencies and serves the FastAPI app with uvicorn.
# All layers are ordered for caching: dependencies first, source code last.
FROM public.ecr.aws/docker/library/python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so this layer is only rebuilt when the pins change.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the application source.
COPY app ./app

# Run as an unprivileged user instead of root.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Health check with the bundled interpreter only: no curl/wget installed.
HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
