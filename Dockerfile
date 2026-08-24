# ---- Base image ----
FROM python:3.11-slim AS base

# Prevents Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- Install dependencies (separate layer for caching) ----
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# ---- Copy application source ----
COPY app/ ./app/
COPY alembic/ ./alembic/

# Create a non-root user to run the container (security best practice)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Basic container health check hitting the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
