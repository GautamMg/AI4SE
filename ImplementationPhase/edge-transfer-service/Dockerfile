FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV EDGE_DB_PATH=/app/edge_transfer.db
ENV API_TOKEN=secret-token
ENV HPC_STORAGE_DIR=/app/hpc_storage

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
