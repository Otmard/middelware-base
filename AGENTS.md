# AGENTS.md

## App Overview

FastAPI middleware service integrating with Odoo and BCP (financial institution). Python 3.14.3.

## Architecture

```
app/
  main.py          # FastAPI app, global exception handlers, OpenAPI schema
  core/            # Config, errors, logging, middleware
  routes/          # API route modules (router pattern)
  services/        # Business logic (injected via Depends)
  schemas/         # Pydantic models
```

## Key Patterns

### Error Handling
- Use `AppException(ErrorRegistry.ERROR_NAME)` instead of raising generic exceptions
- `ErrorRegistry` is the canonical source for all error codes, statuses, and messages
- Routes do NOT contain try/except; exceptions bubble to global handlers
- `global_exception_handler` at line 32 of `app/core/error_handler.py` has a bug: `exc.error` will raise AttributeError on non-AppException exceptions

### Service Dependency Injection
```python
def get_service():
    return ServiceClass()

@router.get("", service: ServiceClass = Depends(get_service))
```

### Configuration
- All config via `pydantic-settings` from `.env`
- Odoo credentials required: `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`
- Do NOT commit `.env` (gitignored)

## Running

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production (Docker)
docker compose up --build
```

## Logs

Written to `logs/app.log` (rotated, 5MB max, 5 backups). JSON formatted in production.

## BCP Endpoint

Planned in `docs/Planeación de endpoints.md`. Not yet implemented. Key spec:
- `POST /api/consulta-cliente` with `Cabecera` (auth) + `CargaUtil` (query params)
- Error codes: "000" success, "100" auth, "200" invalid params, "301" not found, "999" internal

## Missing

- No tests (`pytest` not in requirements)
- No lint/typecheck tooling
- No pre-commit hooks
