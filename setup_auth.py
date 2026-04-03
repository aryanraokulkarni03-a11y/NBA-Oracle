from __future__ import annotations

import getpass

from nba_oracle.auth import generate_secret_key, hash_password
from nba_oracle.env import upsert_dotenv_values


def main() -> None:
    password = getpass.getpass("Set your dashboard password: ")
    confirm = getpass.getpass("Confirm your dashboard password: ")
    if not password:
        raise SystemExit("Password cannot be empty.")
    if password != confirm:
        raise SystemExit("Passwords did not match.")

    env_path = upsert_dotenv_values(
        {
            "ORACLE_PASSWORD_HASH": hash_password(password),
            "ORACLE_SECRET_KEY": generate_secret_key(),
        }
    )
    print(f"Auth bootstrap complete. Updated {env_path}")


if __name__ == "__main__":
    main()
