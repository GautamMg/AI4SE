.PHONY: install run test docker-build docker-run

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q

docker-build:
	docker build -t edge-transfer-service .

docker-run:
	docker run --rm -p 8000:8000 edge-transfer-service
