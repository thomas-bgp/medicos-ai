FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/

# Create data directory and generate POA-only database at build time
RUN mkdir -p data && python backend/seed_poa.py

EXPOSE 8000

# Set default env var so pydantic-settings doesn't crash on startup without .env
# The actual key is injected via Coolify environment variables at runtime
ENV ANTHROPIC_API_KEY="placeholder-set-in-coolify"

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
