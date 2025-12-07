.PHONY: install run test docker-build docker-run

install:
\tpip install -r requirements.txt

run:
\tuvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
\tpytest -q

docker-build:
\tdocker build -t aooct-eng-service .

docker-run:
\tdocker run --rm -p 8000:8000 aooct-eng-service

