"""Create the first admin user, or promote an existing user to admin.

Usage (DATABASE_URL and SECRET_KEY must be set, migrations applied):
    python -m dfhc.scripts.create_admin admin@example.com
The password is read from the DFHC_ADMIN_PASSWORD env var, or prompted for.
"""

import getpass
import os
import sys

from dfhc.app.core.database import SessionLocal
from dfhc.app.repositories import users as user_repo
from dfhc.app.schemas import UserCreate


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m dfhc.scripts.create_admin <email>", file=sys.stderr)
        return 2
    email = argv[1].strip()

    db = SessionLocal()
    try:
        user = user_repo.get_user_by_email(db, email)
        if user:
            user.is_superuser = True
            user.is_active = True
            db.commit()
            print(f"Promoted existing user {email} to admin.")
            return 0

        password = os.getenv("DFHC_ADMIN_PASSWORD") or getpass.getpass("Admin password: ")
        user_in = UserCreate(email=email, password=password, full_name="Administrator")
        user_repo.create_user(db, user_in, is_superuser=True)
        print(f"Created admin user {email}.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
