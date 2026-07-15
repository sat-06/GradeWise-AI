"""GradeWise AI - Knowledge Base Routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.repositories.repositories import (
    GradeTransitionRepository,
    PaperGradeRepository,
)
from app.schemas.schemas import GradeTransitionResponse, TransitionSearchRequest

router = APIRouter()


@router.get("/transitions", response_model=list[GradeTransitionResponse])
async def list_transitions(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all grade transitions."""
    repo = GradeTransitionRepository(db)
    return list(await repo.get_all(limit=limit))


@router.post("/transitions/search", response_model=list[GradeTransitionResponse])
async def search_transitions(
    request: TransitionSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search for similar grade transitions by GSM values."""
    repo = GradeTransitionRepository(db)
    grade_repo = PaperGradeRepository(db)

    from_grade_id = None
    to_grade_id = None

    if request.from_gsm:
        from_grade = await grade_repo.get_by_gsm(request.from_gsm)
        if from_grade:
            from_grade_id = from_grade.id

    if request.to_gsm:
        to_grade = await grade_repo.get_by_gsm(request.to_gsm)
        if to_grade:
            to_grade_id = to_grade.id

    transitions = await repo.search_transitions(
        from_grade_id=from_grade_id,
        to_grade_id=to_grade_id,
        success=request.success,
        limit=request.limit,
    )

    return list(transitions)


@router.get("/transitions/{transition_id}", response_model=GradeTransitionResponse)
async def get_transition(transition_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific grade transition."""
    repo = GradeTransitionRepository(db)
    transition = await repo.get_by_id(transition_id)
    if not transition:
        raise HTTPException(404, "Transition not found")
    return transition


@router.get("/transitions/similar", response_model=list[GradeTransitionResponse])
async def find_similar_transitions(
    from_gsm: float = Query(...),
    to_gsm: float = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Find similar historical grade transitions."""
    repo = GradeTransitionRepository(db)
    return list(await repo.get_similar_transitions(from_gsm, to_gsm, limit=limit))


@router.get("/best-practices")
async def get_best_practices(
    from_gsm: Optional[float] = Query(None),
    to_gsm: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get best practices and lessons learned from historical transitions."""
    repo = GradeTransitionRepository(db)

    transitions = await repo.get_all(limit=200)
    successful = [t for t in transitions if t.success and t.lessons_learned]

    if from_gsm and to_gsm:
        grade_repo = PaperGradeRepository(db)
        from_grade = await grade_repo.get_by_gsm(from_gsm)
        to_grade = await grade_repo.get_by_gsm(to_gsm)
        if from_grade and to_grade:
            successful = [
                t for t in successful
                if t.from_grade_id == from_grade.id and t.to_grade_id == to_grade.id
            ]

    practices = []
    for t in successful[:10]:
        practices.append({
            "transition_id": str(t.id),
            "from_grade": str(t.from_grade_id),
            "to_grade": str(t.to_grade_id),
            "stabilization_time_seconds": t.stabilization_time_seconds,
            "parameter_settings": t.parameter_settings,
            "lessons_learned": t.lessons_learned,
            "success": t.success,
        })

    return {
        "best_practices": practices,
        "summary": {
            "average_stabilization_time": (
                sum(t.stabilization_time_seconds or 0 for t in successful) / max(len(successful), 1)
            ),
            "success_rate": (
                len([t for t in successful if t.success]) / max(len(successful), 1) * 100
            ),
            "total_successful_transitions": len(successful),
        },
    }
