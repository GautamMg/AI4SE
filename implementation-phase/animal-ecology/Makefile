.PHONY: run test docker-build docker-run

run:
	uvicorn app.main:app --reload

test:
	pytest -q

docker-build:
	docker build -t configadminapi-slice .

docker-run:
	docker run --rm -p 8000:8000 configadminapi-slice
