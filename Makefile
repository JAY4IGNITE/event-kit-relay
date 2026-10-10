.PHONY: up down logs migrate revision backend-test frontend-gen fmt

up:            ## start db + backend + frontend
	docker compose up --build

down:          ## stop and remove containers
	docker compose down

logs:
	docker compose logs -f backend

migrate:       ## apply migrations inside the backend container
	docker compose exec backend alembic upgrade head

revision:      ## autogenerate a migration: make revision m="message"
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

backend-test:
	docker compose exec backend pytest -q

frontend-gen:  ## regenerate TS types from the backend OpenAPI schema
	cd frontend && npm run gen:api

fmt:
	cd backend && ruff format app tests
