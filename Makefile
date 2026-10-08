.PHONY: backend-install backend-test backend-run frontend-install frontend-test frontend-build dev

backend-install:
	cd backend && pip install -e .[test]

backend-test:
	cd backend && pytest

backend-run:
	cd backend && uvicorn app.main:app --reload

frontend-install:
	cd frontend && npm install

frontend-test:
	cd frontend && npm run test

frontend-build:
	cd frontend && npm run build

dev:
	docker compose up --build
