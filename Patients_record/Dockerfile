ARG PYTHON_VERSION=3.13.14
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATIENTS_FILE=/app/data/patients.json

WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt && \
    adduser --disabled-password --gecos "" --uid 10001 appuser

COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser patients.json ./data/patients.json

USER appuser

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
