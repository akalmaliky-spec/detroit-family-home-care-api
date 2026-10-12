# Authentication and authorization

## Credential flow

`POST /users/` registers a regular user; public registration never grants administrator privileges. Passwords must be 10-256 characters and at most 72 UTF-8 bytes. Creation and updates enforce the same policy. Only bcrypt hashes are stored or compared; hashes never appear in responses.

`POST /auth/token` accepts form fields `username` (email) and `password`. Active users receive an HS256 access JWT, an opaque refresh token, and `expires_in` seconds. Access JWTs contain an immutable user ID (`sub`), expiry (`exp`), issue time (`iat`), token type and account token version (`ver`). `SECRET_KEY` from the environment is the sole signing key; missing, short and recognized placeholder keys prevent startup even in testing when explicitly supplied. Generate production secrets with `openssl rand -hex 32`.

Send access tokens as `Authorization: Bearer <token>`. Never place tokens in URLs or logs. Token responses use `Cache-Control: no-store`. This API does not set cookies or choose browser storage. A browser integration must design its own secure credential storage; do not persist refresh tokens in localStorage. Wix member sessions and Wix service API keys are separate identities and cannot be used as these JWTs.

`POST /auth/refresh` accepts JSON `{ "refresh_token": "..." }`. Refresh tokens have 384 bits of random entropy; only their SHA-256 digests are stored in `refresh_sessions`. Successful refresh revokes the presented token and returns a fresh pair. Expired, revoked and reused refresh tokens are rejected. The configured PostgreSQL deployment serializes refresh/password-reset/logout using row locks.

`POST /auth/logout` requires an access token and invalidates **all sessions for that user**. Password changes and active-status changes also invalidate all access and refresh tokens by incrementing the account token version and revoking refresh records. Deleted or inactive users cannot authenticate. No legacy email-subject/default-key JWTs are accepted after this change.

Defaults: access tokens 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`, range 1-1440); refresh tokens 7 days (`REFRESH_TOKEN_EXPIRE_DAYS`, range 1-30).

## Permissions

| Operation | Required identity |
| --- | --- |
| Register, login, health | Public |
| Read/update `/users/me` | Active user; self-update permits only name/password |
| List/read/update/delete `/users/{id}` | Active administrator |
| Create client | Active administrator |
| List/read/update/delete clients | Active administrator, or the assigned owner |
| Assign/change client owner | Active administrator; owner must be an active user |

Unauthorized record access returns 404 without disclosing whether a client exists. Existing clients migrate with a null `owner_user_id` and remain admin-only until assigned; no automatic ownership inference is performed. Owner assignment is via admin client creation/PATCH. Configure assignment only for authorized staff or client accounts. Backend checks apply independently of frontend page access.

## Rollout

1. Generate a new environment `SECRET_KEY`; the formerly hardcoded key is compromised by design and must never be reused.
2. Run `alembic upgrade head` before starting the application. Revision 0003 adds token versions, refresh sessions and client ownership while retaining records.
3. With database operator access, run `python -m dfhc.bootstrap_admin --email YOUR_ADMIN_EMAIL`. New accounts prompt for a password; existing accounts are promoted and their sessions revoked. There is no remote public bootstrap route.
4. Assign client owners through an administrator account. Legacy records stay inaccessible to regular users until assigned.
5. Require HTTPS at the deployment edge and keep `TESTING` unset/false in production. Update integrations for the new token response and immutable-subject tokens.
6. Run the post-deployment smoke checks. Confirm guests get 401, ordinary users get 403 on administration, and cross-user client access is denied.

Login and refresh are limited to 10 attempts per source IP per minute per process. The in-memory limiter does not coordinate multiple workers and intentionally does not trust raw X-Forwarded-For. Use a shared/edge limiter and correctly configured trusted proxy handling for production scaling. Review public registration policy and add invitation/email verification if required by the deployment. Periodically delete expired/revoked refresh rows under your retention policy; do not log token values.
