#!/usr/bin/env python3

# Filename: setup_app.py
#
# Description: This script provides an all-in-one script to build the database,
# add sample data to the database, and run the app. This is in contrast to
# running the set up scripts individually so using/developing/debugging this
# app should be significantly easier.
#
# Parent: none
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"

def venv_python() -> str:
    return str(VENV_DIR / "bin" / "python")

def run(args) -> None:
    print(f"==> {' '.join(str(a) for a in args)}")
    subprocess.run(args, check=True)

def main() -> None:
    os.chdir(ROOT)

    # Create a virtual environment if it doesn't exist.
    if not VENV_DIR.exists():
        print("==> Creating virtual environment (.venv)")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])

    py = venv_python()

    # Install dependencies into the venv.
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "-r", "requirements.txt"])

    # Build the database. Safe to run even if the database already exists.
    run([py, "db/build_db.py"])

    # Add sample data to the db. Safe to run even if the data already exists.
    run([py, "seed.py"])

    # Launch the app.
    print("==> Starting the app at http://127.0.0.1:5000  (Ctrl+C to stop)")
    subprocess.run([py, "app.py"])

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nA setup step failed (exit code {e.returncode}). See the error above.")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nStopped.")