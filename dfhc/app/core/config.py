import os

_TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")
SECRET_KEY = os.getenv("SECRET_KEY", "ci-test-secret-key-not-for-production-use" if _TESTING else "")
if len(SECRET_KEY.encode("utf-8")) < 32 or any(
    marker in SECRET_KEY.lower() for marker in ("change-me", "replace_with", "your-secret")
):
    raise RuntimeError("SECRET_KEY must be a generated secret of at least 32 bytes")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
if not 1 <= ACCESS_TOKEN_EXPIRE_MINUTES <= 1440 or not 1 <= REFRESH_TOKEN_EXPIRE_DAYS <= 30:
    raise RuntimeError("Token lifetimes must be positive and within the documented bounds")
