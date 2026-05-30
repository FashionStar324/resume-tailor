.PHONY: dev migrate downgrade db-reset

dev:
	uvicorn app.main:app --reload --port 8000

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

db-reset:
	alembic downgrade base && alembic upgrade head
