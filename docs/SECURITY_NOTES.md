# Security notes

Authentication is implemented in `dfhc/app/core/security.py`, `core/sessions.py`, `dependencies/auth.py` and `routes/auth.py`. See [Authentication](AUTHENTICATION.md) for the complete flow, permission matrix and rollout steps.

- JWT signing reads a required environment secret; known placeholders and values shorter than 32 bytes are rejected.
- Passwords use bcrypt; registration and changes enforce the 72-byte limit and minimum 10-character policy.
- Access-token validation requires expiry, issue time, immutable user ID, token type and account version. Disabled/deleted accounts and revoked versions are rejected.
- User administration is admin-only. Client access is checked against an explicit owner or administrator; public registration does not authorize access to client data.
- Opaque refresh tokens are hashed in the database and rotate on every refresh. Logout, password and activation changes revoke account sessions.
- SQLAlchemy parameterized queries are used. Environment secrets and token responses must stay out of logs and source control.

Deployment requirements: HTTPS, migrations, a newly generated JWT secret, explicitly bootstrapped administrators, explicit client assignment, and a shared/edge auth limiter when running multiple processes. Application CORS permits only configured origins, bearer headers and supported methods; CORS does not replace authorization.

Remaining production work includes invitation/email-verification policy, MFA for privileged accounts, monitoring, and refresh-session retention. No HIPAA compliance certification is implied by these controls.
