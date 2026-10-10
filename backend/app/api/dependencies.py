"""One mutation boundary for the local dashboard and background sweeps."""
import asyncio
from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app.infrastructure.db.base import get_session
from app.infrastructure.db.dashboard import sweep

dashboard_lock = asyncio.Lock()


async def dashboard_session(
    session: AsyncSession = Depends(get_session),
) -> AsyncIterator[AsyncSession]:
    async with dashboard_lock:
        try:
            await sweep(session)
            yield session
        except (IntegrityError, StaleDataError) as exc:
            await session.rollback()
            raise HTTPException(409, "Reservation changed concurrently; please retry") from exc
        except OperationalError as exc:
            await session.rollback()
            if "locked" in str(exc).lower():
                raise HTTPException(409, "Database is busy; please retry") from exc
            raise
