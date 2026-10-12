"""Run locally with database operator access: python -m dfhc.bootstrap_admin --email ..."""
import argparse
from getpass import getpass
from dfhc.app.core.database import SessionLocal
from dfhc.app.core.sessions import revoke_user_sessions
from dfhc.app.core.security import get_password_hash
from dfhc.app.models import User
from dfhc.app.schemas import UserCreate


def main():
    parser = argparse.ArgumentParser(description="Create or promote an administrator using operator database access")
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == args.email).with_for_update().first()
        if user is None:
            body = UserCreate(email=args.email, password=getpass("New admin password: "))
            user = User(email=body.email, hashed_password=get_password_hash(body.password), token_version=0)
            db.add(user)
            db.flush()
        revoke_user_sessions(db, user)
        user.is_superuser = True
        user.is_active = True
        db.commit()
    print("Administrator configured; existing sessions revoked.")


if __name__ == "__main__":
    main()
