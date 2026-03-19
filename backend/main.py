import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.routers.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify the database file exists
    db_path = settings.DB_PATH
    if not os.path.exists(db_path):
        raise RuntimeError(
            f"Banco de dados não encontrado em '{db_path}'. "
            "Execute o script de seed antes de iniciar o servidor."
        )
    print(f"[startup] Banco de dados encontrado: {db_path}")
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="Médicos AI",
    description="API para busca inteligente de médicos via linguagem natural",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins so the frontend (served separately in dev) works
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(chat_router)

# Serve the frontend as static files at "/"
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_dir = os.path.abspath(frontend_dir)

if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    print(f"[warning] Diretório frontend não encontrado: {frontend_dir}")


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
