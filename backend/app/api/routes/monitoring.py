"""GradeWise AI - Live Monitoring Routes."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.repositories.repositories import (
    PaperGradeRepository,
    ProductionRunRepository,
    SensorReadingRepository,
)
from app.schemas.schemas import (
    PaperGradeResponse,
    ProductionRunCreate,
    ProductionRunResponse,
    SensorReadingCreate,
    SensorReadingResponse,
)

router = APIRouter()


# ── Production Runs ───────────────────────────────────

@router.get("/runs", response_model=list[ProductionRunResponse])
async def list_production_runs(
    machine_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List production runs with optional filters."""
    repo = ProductionRunRepository(db)

    if machine_id:
        runs = await repo.get_runs_by_machine(machine_id, limit=limit)
    elif status:
        if status == "active":
            runs = await repo.get_active_runs()
        else:
            runs = await repo.get_all(limit=limit)
    else:
        runs = await repo.get_all(limit=limit)

    return list(runs)


@router.get("/runs/active", response_model=list[ProductionRunResponse])
async def get_active_runs(db: AsyncSession = Depends(get_db)):
    """Get all currently active production runs."""
    repo = ProductionRunRepository(db)
    return list(await repo.get_active_runs())


@router.post("/runs", response_model=ProductionRunResponse)
async def create_production_run(
    data: ProductionRunCreate,
    db: AsyncSession = Depends(get_db),
):
    """Start a new production run."""
    from app.models.models import ProductionRun

    repo = ProductionRunRepository(db)
    run = ProductionRun(**data.model_dump())
    return await repo.create(run)


@router.get("/runs/{run_id}", response_model=ProductionRunResponse)
async def get_production_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ProductionRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(404, "Production run not found")
    return run


# ── Sensor Readings ───────────────────────────────────

@router.get("/runs/{run_id}/readings/recent", response_model=list[SensorReadingResponse])
async def get_recent_readings(
    run_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get most recent sensor readings for a run."""
    repo = SensorReadingRepository(db)
    return list(await repo.get_recent(run_id, limit=limit))


@router.get("/runs/{run_id}/readings/latest", response_model=SensorReadingResponse)
async def get_latest_reading(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get the latest sensor reading."""
    repo = SensorReadingRepository(db)
    reading = await repo.get_latest_for_run(run_id)
    if not reading:
        raise HTTPException(404, "No readings found for this run")
    return reading


@router.post("/readings", response_model=SensorReadingResponse)
async def ingest_sensor_reading(
    data: SensorReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a new sensor reading (from plant historian / OPC-UA)."""
    from app.models.models import SensorReading

    repo = SensorReadingRepository(db)
    reading = SensorReading(**data.model_dump())
    return await repo.create(reading)


@router.get("/readings/history", response_model=list[SensorReadingResponse])
async def get_readings_history(
    run_id: UUID = Query(...),
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get sensor readings for a time range."""
    repo = SensorReadingRepository(db)
    return list(await repo.get_time_range(run_id, start_time, end_time))


# ── Paper Grades ─────────────────────────────────────

@router.get("/grades", response_model=list[PaperGradeResponse])
async def list_paper_grades(db: AsyncSession = Depends(get_db)):
    """List all paper grades."""
    repo = PaperGradeRepository(db)
    return list(await repo.get_all(limit=100))
