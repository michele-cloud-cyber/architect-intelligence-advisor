"""
Logger Utility

Simple logging utility for Architect Intelligence Advisor.
"""

from datetime import datetime


class Logger:

    @staticmethod
    def info(message):
        print(f"[INFO] {datetime.now()} - {message}")

    @staticmethod
    def warning(message):
        print(f"[WARNING] {datetime.now()} - {message}")

    @staticmethod
    def error(message):
        print(f"[ERROR] {datetime.now()} - {message}")
