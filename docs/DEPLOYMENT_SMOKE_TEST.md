# DFHC API post-deployment smoke test

Run migrations and configure an administrator as described in [Authentication](AUTHENTICATION.md). Never create a fixed production account/password from examples.

Run `bash scripts/smoke_test.sh https://YOUR-API-DOMAIN`. The script performs read-only health and unauthenticated-access checks, and optionally checks a supplied access token without printing it. Supply a regular user's token through `DFHC_SMOKE_ACCESS_TOKEN` and set `DFHC_SMOKE_ROLE=member`; supply an administrator token and set the role to `admin` for admin checks. Do not use shell tracing or paste real credentials into issue comments.

Expected behavior:

- `/health`: 200; docs expose auth, user and client routes.
- `/users/` and `/clients/` without credentials: 401.
- `/users/me` with a valid token: 200.
- `/users/` with a member token: 403; with an admin token: 200.
- `/clients/` with a valid token: 200, scoped to ownership for members.

In a staging database, additionally verify refresh rotation/replay rejection, password-reset/logout revocation, inactive-account denial and cross-user read/update/delete denial. Do not create medical test records in production. Automated regressions cover these cases in `dfhc/tests/test_auth_security.py`.

Stop rollout if migrations fail, a secret is rejected, a public protected route returns data, the owner scope is incorrect, or refresh/revocation fails. Do not claim the frontend is integrated until authenticated requests have been tested on the published deployment.
