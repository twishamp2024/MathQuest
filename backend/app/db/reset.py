"""Development-only database reset utility.

Requires explicit confirmation flag to prevent accidental loss of learner history.
NEVER called automatically on application startup.
"""

import sys
import argparse
from backend.app.db.base import Base
from backend.app.db.session import engine, init_db


def reset_database(force: bool = False) -> bool:
    """Drop all tables and recreate them if force is True."""
    if not force:
        print("ERROR: Refusing to reset database without explicit --confirm-reset flag.")
        return False

    print("WARNING: Dropping all database tables...")
    from backend.app.db import models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
    print("Recreating database tables...")
    init_db()
    print("Database reset completed successfully.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MathQuest Database Reset Utility")
    parser.add_argument(
        "--confirm-reset",
        action="store_true",
        help="Explicitly confirm dropping and recreating all database tables",
    )
    args = parser.parse_args()

    success = reset_database(force=args.confirm_reset)
    sys.exit(0 if success else 1)
