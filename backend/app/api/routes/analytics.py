"""GradeWise AI - Analytics & KPI Routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.repositories.repositories import (
    AlertRepository,
    GradeTransitionRepository,
    PredictionRepository,
    RecommendationRepository,
)
from app.schemas.schemas import KPIData

router = APIRouter()


@router.get("/kpi", response_model=KPIData)
async def get_kpi_dashboard(db: AsyncSession = Depends(get_db)):
    """Get business intelligence KPI data for the dashboard."""
    pred_repo = PredictionRepository(db)
    rec_repo = RecommendationRepository(db)
    alert_repo = AlertRepository(db)
    transition_repo = GradeTransitionRepository(db)

    predictions = await pred_repo.get_all(limit=1000)
    recommendations = await rec_repo.get_all(limit=1000)

    total_preds = len(predictions)
    total_recs = len(recommendations)

    # Calculate acceptance rate
    accepted = sum(1 for r in recommendations if r.status == "accepted")
    modified = sum(1 for r in recommendations if r.status == "modified")
    acceptance_rate = (accepted + modified) / max(total_recs, 1) * 100

    # Calculate recommendation success rate (accepted + applied)
    applied = sum(1 for r in recommendations if r.status == "applied")
    success_rate = (accepted + applied) / max(total_recs, 1) * 100

    # Average confidence
    avg_confidence = sum(p.confidence_score for p in predictions) / max(total_preds, 1)

    # Average stabilization time
    avg_stab = sum(
        p.estimated_stabilization_time
        for p in predictions
        if p.estimated_stabilization_time
    ) / max(len([p for p in predictions if p.estimated_stabilization_time]), 1)

    transitions = await transition_repo.get_all(limit=500)
    successful_transitions = sum(1 for t in transitions if t.success)

    # Estimate waste metrics
    estimated_waste_reduced = total_recs * 12.5  # kg per recommendation
    paper_saved = estimated_waste_reduced * 0.85
    production_efficiency = 85.0 + (success_rate * 0.15)

    return KPIData(
        estimated_waste_reduced_kg=round(estimated_waste_reduced, 1),
        paper_saved_kg=round(paper_saved, 1),
        production_efficiency=round(production_efficiency, 1),
        average_stabilization_time=round(avg_stab, 1),
        operator_acceptance_rate=round(acceptance_rate, 1),
        recommendation_success_rate=round(success_rate, 1),
        total_predictions=total_preds,
        total_recommendations=total_recs,
        total_alerts=len(await alert_repo.get_all(limit=1000)),
        average_confidence=round(avg_confidence, 2),
    )
