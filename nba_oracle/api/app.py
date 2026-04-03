from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from nba_oracle.api.routes import auth, health, learning, operator, picks, providers, stability, today


def build_app() -> FastAPI:
    app = FastAPI(
        title="NBA Oracle API",
        version="0.4.0",
        summary="Operating core for the NBA Oracle backend.",
    )

    @app.get("/")
    def root() -> dict[str, object]:
        return {
            "name": "NBA Oracle",
            "phase": "4A",
            "status": "operating_core",
            "docs": {
                "health": "/api/health",
                "today": "/api/today",
                "login": "/api/auth/login",
            },
        }

    @app.exception_handler(ValueError)
    def handle_value_error(_, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(RuntimeError)
    def handle_runtime_error(_, exc: RuntimeError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    app.include_router(auth.router)
    app.include_router(health.router)
    app.include_router(today.router)
    app.include_router(picks.router)
    app.include_router(stability.router)
    app.include_router(learning.router)
    app.include_router(providers.router)
    app.include_router(operator.router)
    return app
