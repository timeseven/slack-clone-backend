default: 
  just --list

run *args: 
  uv run uvicorn app.main:app --reload {{args}}

arq:
  uv run arq app.core.arq_worker.WorkerSettings

mm *args: 
  uv run alembic revision --autogenerate -m "{{args}}"

migrate: 
  uv run alembic upgrade head

downgrade *args: 
  uv run alembic downgrade {{args}}

ruff *args: 
  uv run ruff check {{args}} app

lint: 
  uv run ruff format app
  just ruff --fix
