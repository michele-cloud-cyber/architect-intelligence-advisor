"""Streamlit Community Cloud entry point for the demo-only application."""

from pathlib import Path
from runpy import run_path


run_path(str(Path(__file__).parent / "dashboard_v2" / "app.py"), run_name="__main__")
