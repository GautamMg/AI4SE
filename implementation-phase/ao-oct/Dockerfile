FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY openapi_slice.yaml .
COPY README.md .

ENV ENG_DB_PATH=/app/aooct_eng.db
ENV API_TOKEN=secret-token
ENV ENG_STORAGE_DIR=/app/eng_storage
ENV MAX_UPLOAD_BYTES=5242880
ENV RANDOM_SEED=1234

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

