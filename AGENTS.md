# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: FastAPI entrypoint (mounts routers under `/api`, initializes DB on startup).
- `app/`: backend package
  - `routes/`: API endpoints
  - `services/`: business logic (e.g., report review workflow)
  - `models/`: SQLModel models/enums
  - `auth/`: JWT auth + dependencies
  - `utils/`: file handling + workflow helpers
- `data/`: runtime data (SQLite at `data/app.db`, uploaded reports under `data/reports/`).
- `frontend/`: Vite + Vue 3 app (`frontend/src/` for code, `frontend/public/` for assets).
- `docs/`: architecture and API documentation.

## Build, Test, and Development Commands
Backend (from repo root):
- `python -m pip install -r requirements.txt` — install backend dependencies.
- `python main.py` — run API with autoreload (Uvicorn).
- `uvicorn main:app --reload --port 8000` — equivalent dev server command.
- `python migrate_database.py` — one-off migration script; backs up then modifies `data/app.db`.

Frontend:
- `cd frontend && npm install` — install frontend dependencies.
- `npm run dev` — start Vite dev server.
- `npm run build` — production build to `frontend/dist/`.
- `npm run preview` — preview the production build locally.

## Coding Style & Naming Conventions
- Python: 4-space indentation, use type hints where practical. Keep routing thin; prefer `app/services/` for workflow logic. Use `snake_case` for modules/functions and `PascalCase` for classes.
- Frontend: follow existing style in `frontend/src/` (2-space indentation, single quotes, no semicolons). Vue components use `PascalCase` filenames (e.g., `MainLayout.vue`).
- Formatting/linting: no repo-wide formatter configured; match surrounding code style.

## Testing Guidelines
- No dedicated test suite is committed yet. If adding non-trivial backend logic, create `pytest` tests under `tests/` named `test_*.py`.
- For frontend UI changes, include a brief manual verification checklist (routes exercised, roles tested).

## Commit & Pull Request Guidelines
- Repo has no existing Git history. Use a consistent convention going forward; recommended: Conventional Commits (e.g., `feat(frontend): add report filter`, `fix(backend): validate period format`).
- PRs: include a short description, steps to test, screenshots for UI changes, and call out any DB-impacting changes (especially anything touching `data/` or migrations).

## Security & Configuration Tips
- Backend reads `.env` (see `app/config.py`); never commit real `SECRET_KEY` values.
- Frontend API base URL uses `VITE_API_BASE_URL` (see `frontend/src/utils/request.js`).

## Agent-Specific Instructions
- Treat `data/`, `__pycache__/`, `venv/`, and `frontend/node_modules/` as generated/runtime artifacts; avoid editing or committing them unless explicitly required.
