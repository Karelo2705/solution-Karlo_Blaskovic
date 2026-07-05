.PHONY: run migrate revision test freeze docker-build docker-up docker-down docker-logs

run:
	python -m uvicorn src.app.main:app --reload

migrate:
	python -m alembic upgrade head

revision:
	python -m alembic revision --autogenerate -m "$(m)"

test:
	pytest

freeze:
	pip freeze > requirements.txt

docker-build:
	docker build -t tickethub-api .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api
