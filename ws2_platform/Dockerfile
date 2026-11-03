# API image (Hugging Face Spaces Docker or Render). Build from the repo root:
#   docker build -f ws2_platform/Dockerfile -t fire-api .
#   docker run -p 7860:7860 fire-api
# The API's data files are baked into the image (decision 10); run the pipeline first on the build machine.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY common/ common/
COPY ws2_platform/ ws2_platform/
COPY ws3_anomaly/ ws3_anomaly/
COPY ws4_outlook/ ws4_outlook/
COPY ws1_harmonize/ ws1_harmonize/
COPY tools/ tools/
COPY contracts/ contracts/
# Only what the API reads (all under 10 MB, so no Git LFS on Hugging Face). detections, grid_daily and
# predictions_oof are not needed at runtime.
COPY data/processed/cells.parquet data/processed/harmonized.parquet data/processed/sensor_days.parquet \
     data/processed/interval_table.json data/processed/drivers_region.json data/processed/outlook_region.json \
     data/processed/
COPY data/processed/validation/ data/processed/validation/
ENV DATA_DIR=/app/data/processed PORT=7860
EXPOSE 7860
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')"
CMD ["sh", "-c", "uvicorn ws2_platform.api.app:app --host 0.0.0.0 --port ${PORT}"]
