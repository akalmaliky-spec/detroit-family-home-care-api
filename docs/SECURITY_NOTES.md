# Security Notes — Threat Model (MVP)

## Assets

| Asset | Risk if compromised |
|-------|--------------------|
| JWT secret key () | Token forgery — attacker can impersonate any user |
| User password hashes | Offline brute-force attacks |
| Database data (users, PII) | Privacy breach, regulatory exposure |
| Database URL / credentials | Full DB access |

## Entry Points

| Endpoint | Risk |
|----------|------|
|  | Brute-force credential stuffing |
|  | Account enumeration, malformed input |
|  | Unauthorized data access (no auth check yet) |
|  | Privilege escalation if no ownership check |
|  | Account destruction if no ownership check |

## Top Risks (OWASP-aligned)

1. **Brute force / credential stuffing** on  — no rate limit yet.
2. **Weak JWT secret** — default  must never reach production.
3. **Token theft** — JWTs are long-lived; no refresh/revocation mechanism yet.
4. **SQLi** — mitigated by SQLAlchemy ORM parameterized queries. Do not use raw SQL.
5. **Misconfiguration** —  accidentally committed;  in logs.
6. **Password policy gaps** — MVP enforces minimum length; needs iteration.

## Mitigations in Place (Phase 6-7)

- Passwords hashed with bcrypt (work factor >= 12 rounds via passlib default).
- JWT expiry enforced ().
- On startup: if  is the default dev value, app raises  (non-test envs).
- Password policy: minimum 10 chars, maximum 256 chars (anti-bcrypt-DoS).
- bcrypt pinned  to prevent passlib compatibility issues.
-  in ;  contains only placeholders.
- SQLAlchemy ORM used exclusively — no raw SQL in codebase.

## TODO (future phases)

- [ ] Add rate limiting on  (e.g., ).
- [ ] Add JWT refresh token + revocation (blocklist in Redis).
- [ ] Add per-user ownership checks on PATCH/DELETE.
- [ ] Enable HTTPS-only (handled at infra level).
- [ ] Add SAST scan to CI (e.g., usage: bandit [-h] [-r] [-a {file,vuln}] [-n CONTEXT_LINES] [-c CONFIG_FILE]
              [-p PROFILE] [-t TESTS] [-s SKIPS]
              [-l | --severity-level {all,low,medium,high}]
              [-i | --confidence-level {all,low,medium,high}]
              [-f {csv,custom,html,json,screen,txt,xml,yaml}]
              [--msg-template MSG_TEMPLATE] [-o [OUTPUT_FILE]] [-v] [-d] [-q]
              [--ignore-nosec] [-x EXCLUDED_PATHS] [-b BASELINE]
              [--ini INI_PATH] [--exit-zero] [--version]
              [targets ...]).
- [ ] Enable GitHub secret scanning + push protection.
