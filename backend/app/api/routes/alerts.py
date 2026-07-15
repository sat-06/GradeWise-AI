"""GradeWise AI - Alert Routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.repositories.repositories import AlertRepository
from app.schemas.schemas import AlertResponse

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    production_run_id: UUID = Query(None),
    priority: str = Query(None),
    unacknowledged_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List alerts with optional filters."""
    repo = AlertRepository(db)

    if unacknowledged_only:
        alerts = await repo.get_unacknowledged(limit=limit)
    elif priority:
        alerts = await repo.get_by_priority(priority, limit=limit)
    elif production_run_id:
        alerts = await repo.get_by_run(production_run_id, limit=limit)
    else:
        alerts = await repo.get_all(limit=limit)

    return list(alerts)


@router.get("/unacknowledged", response_model=list[AlertResponse])
async def get_unacknowledged_alerts(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get all unacknowledged alerts."""
    repo = AlertRepository(db)
    return list(await repo.get_unacknowledged(limit=limit))


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an alert."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")

    from datetime import UTC, datetime

    alert.is_acknowledged = True
    alert.acknowledged_at = datetime.now(UTC)
    await repo.update(alert)

    return {"status": "acknowledged"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Mark an alert as resolved."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")

    alert.is_resolved = True
    alert.is_acknowledged = True
    await repo.update(alert)

    return {"status": "resolved"}
