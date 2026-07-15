"""GradeWise AI - Recommendation Routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.models import Recommendation
from app.repositories.repositories import (
    PredictionRepository,
    RecommendationRepository,
)
from app.schemas.schemas import (
    OperatorFeedback,
    RecommendationResponse,
)

router = APIRouter()


@router.get("/", response_model=list[RecommendationResponse])
async def list_recommendations(
    production_run_id: UUID = Query(...),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get recommendations for a production run."""
    repo = RecommendationRepository(db)
    return list(await repo.get_by_run(production_run_id, limit=limit))


@router.get("/pending", response_model=list[RecommendationResponse])
async def get_pending_recommendations(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending recommendations requiring operator action."""
    repo = RecommendationRepository(db)
    return list(await repo.get_pending(limit=limit))


@router.post("/{recommendation_id}/feedback")
async def submit_feedback(
    recommendation_id: UUID,
    feedback: OperatorFeedback,
    db: AsyncSession = Depends(get_db),
):
    """Submit operator feedback on a recommendation."""
    repo = RecommendationRepository(db)
    rec = await repo.get_by_id(recommendation_id)

    if not rec:
        raise HTTPException(404, "Recommendation not found")

    if feedback.action == "accept":
        rec.status = "accepted"
    elif feedback.action == "reject":
        rec.status = "rejected"
    elif feedback.action == "modify":
        rec.status = "modified"
        if feedback.modified_settings:
            rec.modified_settings = feedback.modified_settings

    rec.operator_feedback = feedback.comments
    await repo.update(rec)

    return {"status": "ok", "new_status": rec.status}


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific recommendation."""
    repo = RecommendationRepository(db)
    rec = await repo.get_by_id(recommendation_id)
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    return rec


@router.post("/generate/{prediction_id}", response_model=RecommendationResponse)
async def generate_recommendation_from_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate optimal recommendations from a prediction."""
    pred_repo = PredictionRepository(db)
    prediction = await pred_repo.get_by_id(prediction_id)

    if not prediction:
        raise HTTPException(404, "Prediction not found")

    # Generate recommendations based on the prediction's feature importance and input
    from app.ml.pipeline.recommendation_engine import RecommendationEngine

    engine = RecommendationEngine()
    input_params = prediction.input_parameters or {}
    target_gsm = 100.0  # Default; in production, look up from production run's target grade
    predicted_gsm = prediction.predicted_basis_weight
    feature_importance = prediction.feature_importance or {}
    confidence = prediction.confidence_score

    result = engine.generate_recommendations(
        current_values=input_params,
        predicted_gsm=predicted_gsm,
        target_gsm=target_gsm,
        feature_importance=feature_importance,
        confidence=confidence,
    )

    # Save recommendation
    rec_repo = RecommendationRepository(db)
    recommendation = Recommendation(
        prediction_id=prediction_id,
        production_run_id=prediction.production_run_id,
        recommended_settings=result["recommended_settings"],
        expected_basis_weight=result["expected_basis_weight"],
        expected_improvement=result["expected_improvement"],
        confidence=result["confidence"],
        reasoning=result["reasoning"],
        status="pending",
    )

    return await rec_repo.create(recommendation)
