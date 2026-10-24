"""Utility to disable blocked Cython .pyd binaries in SQLAlchemy if running under Windows AppControl."""

import os
from pathlib import Path

def ensure_pure_python():
    venv_dir = Path(__file__).resolve().parent.parent / ".venv"
    if not venv_dir.exists():
        return
    sa_dir = venv_dir / "Lib" / "site-packages" / "sqlalchemy"
    if not sa_dir.exists():
        return
    count = 0
    for pyd in sa_dir.rglob("*.pyd"):
        disabled = pyd.with_suffix(".pyd.disabled")
        try:
            pyd.rename(disabled)
            count += 1
        except Exception:
            pass
    if count:
        print(f"Disabled {count} Cython .pyd modules in SQLAlchemy for pure Python compatibility.")

if __name__ == "__main__":
    ensure_pure_python()
