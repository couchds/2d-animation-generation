import os

# Backend URL for generating full URLs to resources
# Default to localhost:8000 but allow override through environment variable
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000") 