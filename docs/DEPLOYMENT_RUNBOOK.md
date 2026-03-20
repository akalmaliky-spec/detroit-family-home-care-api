# DFHC API Deployment Runbook

This runbook is the single source of truth for deploying the Detroit Family Home Care API.

## Goal

Deploy the API safely and only allow frontend integration after backend health, auth, and database checks pass.

## Approved deployment target

- Preferred first target: **Render**
- Acceptable backup: Railway

## Pre-deploy gate

Deployment is **blocked** unless all items below are true:

- `main` contains the latest approved backend changes
- CI is green on `main`
- `DATABASE_URL` is provisioned
- `SECRET_KEY` is set
- Start command includes migrations first
- No frontend is pointing to the live API yet

## Required environment variables

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` (optional but recommended)

## Required start command

```text
alembic upgrade head && uvicorn dfhc.main:app --host 0.0.0.0 --port $PORT
```

## Deploy steps

1. Merge the approved deployment PR into `main`
2. Connect the GitHub repo to Render
3. Apply `render.yaml` blueprint or equivalent settings manually
4. Wait for initial deploy to complete
5. Run the smoke test:

```bash
bash scripts/smoke_test.sh https://YOUR-API-DOMAIN
```

## Launch decision rules

### Launch is APPROVED only if:
- `/health` returns success
- `/docs` loads
- `/auth/token` returns a valid token
- `/clients/` returns `401` without a token
- `/clients/` returns `200` with a valid token
- client creation succeeds with a token

### Launch is BLOCKED if:
- migrations fail
- `/health` fails
- auth token cannot be issued
- `/clients/` is reachable without authentication
- smoke test script fails at any step

## Post-deploy policy

Do **not** connect the Wix frontend until launch is approved.

Only after smoke test success may the next phase begin:
- add the deployed API base URL to the Wix backend integration layer
- keep frontend secrets out of page/public code
- start with `/health` before `/clients`
