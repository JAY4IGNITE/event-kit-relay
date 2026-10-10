"""FastAPI application entrypoint + exception mapping + scheduler lifecycle."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import inventory, relay
from app.config import settings
from app.domain.errors.exceptions import ConcurrencyConflictError, KitRelayError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compose the scheduler here and register the two recurring sweeps:
    #   scheduler.schedule_recurring("pending-expiry", 60s, PendingExpirySweep(...))
    #   scheduler.schedule_recurring("no-show",        60s, NoShowSweep(...))
    #   scheduler.start()
    yield
    # scheduler.shutdown()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(inventory.router)
app.include_router(relay.router)


@app.exception_handler(ConcurrencyConflictError)
async def _conflict(_: Request, exc: ConcurrencyConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"error": "conflict", "detail": str(exc)})


@app.exception_handler(KitRelayError)
async def _domain_error(_: Request, exc: KitRelayError) -> JSONResponse:
    return JSONResponse(
        status_code=422, content={"error": exc.__class__.__name__, "detail": str(exc)}
    )
