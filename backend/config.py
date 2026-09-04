"""
settle Backend Configuration

Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


# --- Server ---
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))

# --- CORS ---
# Comma-separated list of allowed origins
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# --- Database (future) ---
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/settle")

# --- API Keys (future) ---
# OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "")
# GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
# IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")
