FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements*.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
EXPOSE 4050
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 4050"]

FROM base AS production
RUN useradd --system --uid 10001 --create-home agenda
COPY --chown=agenda:agenda . .
USER agenda
EXPOSE 4050
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4050/health', timeout=3)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4050"]
