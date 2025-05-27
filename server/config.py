"""
Configuration settings for the C2 Server.
"""
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ad_penetrator.db")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "server.log")

# C2 Server settings
C2_HOST = os.getenv("C2_HOST", "0.0.0.0")
C2_PORT = int(os.getenv("C2_PORT", "8000")) 