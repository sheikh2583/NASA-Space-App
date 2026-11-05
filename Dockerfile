# One Render service: compile React, then serve it alongside the real FastAPI.
FROM node:22-bookworm-slim AS frontend
WORKDIR /build/ws5_frontend
COPY ws5_frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY ws5_frontend/ ./
COPY docs/science/method_en.md /build/docs/science/
# Override local .env settings: browser requests use this service's own origin.
ENV VITE_API_BASE_URL=/ VITE_DATA_MODE=real
RUN npm test && npm run check:strings && npm run build

FROM python:3.11-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data/processed FRONTEND_DIR=/app/ws5_frontend/dist \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PORT=10000
COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt
COPY common/ common/
COPY ws2_platform/ ws2_platform/
COPY ws3_anomaly/ ws3_anomaly/
COPY ws4_outlook/ ws4_outlook/
COPY scripts/runtime_bundle.py scripts/runtime_bundle.py
COPY deployment/runtime.json deployment/runtime.json
# Versioned, checksum-verified existing data is baked into the image, not trained.
RUN python scripts/runtime_bundle.py fetch --output /app/data/processed
COPY --from=frontend /build/ws5_frontend/dist/ ws5_frontend/dist/
EXPOSE 10000
CMD ["sh", "-c", "uvicorn ws2_platform.api.app:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"]
