# AGENTS.md

FastAPI middleware service. Python 3.x.

## Architecture
```
app/
  main.py          # FastAPI app, global exception handlers
  core/           # Config, errors, logging, middleware
  routes/         # API route modules
  services/       # Business logic (injected via Depends)
  schemas/        # Pydantic models
```

## Critical: Error Handler Bug
`app/core/error_handler.py:32` - `global_exception_handler` accesses `exc.error` which raises `AttributeError` on non-AppException. Fix by accessing `err` instead of `exc.error`:
```python
content={"code": err.code, "message": err.message}  # uses err, NOT exc.error
```

## Key Patterns
- Use `AppException(ErrorRegistry.ERROR_NAME)` - routes have no try/except
- All config via `pydantic-settings` from `.env` (gitignored)

## Required Env Vars
- Odoo: `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`
- Logto: `LOGTO_URL`, `LOGTO_APP_ID`, `LOGTO_APP_SECRET`
- Redis: `REDIS_URL`

## Running
```bash
# Dev
uvicorn app.main:app --reload --port 8000

# Docker
docker compose up --build
```

## Logs
`logs/app.log` (rotated, 5MB max, 5 backups)
