import os

# ---------------------------------------------------------------------------
# SECRET_KEY — required in production, no unsafe fallback
# In CI/testing, set TESTING=true to bypass the startup check in main.py.
# This module always reads from the environment; a missing var fails loudly.
# ---------------------------------------------------------------------------
_TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

if _TESTING:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ci-test-secret-key-not-for-production-use")
else:
    SECRET_KEY = os.environ["SECRET_KEY"]  # raises KeyError if unset in production

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
