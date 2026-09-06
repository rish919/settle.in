"""
settle — FastAPI Application Entry Point

Registers middleware, routers, and provides the root endpoint.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from contextlib import asynccontextmanager
from scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()

# --- Create app ---
app = FastAPI(
    title="settle API",
    description="Backend for the settle Urban Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import cities, health, recommend, alerts

# --- Register routers ---
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(cities.router, prefix="/api", tags=["Cities"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["Recommendations"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])


# --- Root endpoint ---
@app.get("/")
def root():
    """Root endpoint — redirects to API docs."""
    return {
        "message": "Welcome to the settle API",
        "docs": "/docs",
        "health": "/api/health",
    }
