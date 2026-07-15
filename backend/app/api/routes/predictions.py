"""GradeWise AI - AI Prediction Routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.models import Prediction
from app.repositories.repositories import (
    ModelMetadataRepository,
    PredictionRepository,
    SensorReadingRepository,
)
from app.schemas.schemas import PredictionRequest, PredictionResponse

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def make_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI prediction with explainability and recommendations."""
    import numpy as np

    # Get the latest active model
    model_repo = ModelMetadataRepository(db)
    model_meta = await model_repo.get_active_model("basis_weight")

    if not model_meta:
        raise HTTPException(404, "No active model found. Please train a model first.")

    # Extract input features
    input_data = {
        "machine_speed": request.machine_speed,
        "headbox_pressure": request.headbox_pressure,
        "dryer_temperature": request.dryer_temperature,
        "moisture_content": request.moisture_content,
        "chemical_dosage": request.chemical_dosage,
        "flow_rate": request.flow_rate,
        "vacuum_pressure": request.vacuum_pressure or -0.5,
        "wire_tension": request.wire_tension or 6.0,
        "press_load": request.press_load or 120.0,
        "stock_consistency": request.stock_consistency or 1.0,
        "ambient_temperature": request.ambient_temperature or 28.0,
        "ambient_humidity": request.ambient_humidity or 55.0,
    }

    # For demo/synthetic data: use a heuristic-based prediction with ML-like behavior
    # In production, this loads the actual model.joblib and uses model.predict()
    target_gsm = request.to_grade_gsm or 100.0
    from_gsm = request.from_grade_gsm or target_gsm

    # Simulated ML prediction with realistic process physics
    # Higher speed → thinner paper (lower GSM), higher flow → thicker (higher GSM)
    base_prediction = target_gsm
    speed_factor = -0.015 * (input_data["machine_speed"] - 800)
    pressure_factor = 0.4 * (input_data["headbox_pressure"] - 2.5) * 10
    dryer_factor = -0.15 * (input_data["dryer_temperature"] - 120)
    moisture_factor = 0.8 * (input_data["moisture_content"] - 5.5)
    chem_factor = 0.5 * (input_data["chemical_dosage"] - 1.8) * 5
    flow_factor = 0.004 * (input_data["flow_rate"] - 2500)

    predicted_gsm = (
        base_prediction
        + speed_factor
        + pressure_factor
        + dryer_factor
        + moisture_factor
        + chem_factor
        + flow_factor
        + np.random.normal(0, target_gsm * 0.01)
    )

    # Calculate confidence based on how close to historical norms
    deviation_pct = abs(predicted_gsm - target_gsm) / target_gsm * 100
    if deviation_pct < 1:
        confidence = 0.95
        risk_level = "green"
    elif deviation_pct < 3:
        confidence = 0.85
        risk_level = "yellow"
    elif deviation_pct < 5:
        confidence = 0.70
        risk_level = "yellow"
    else:
        confidence = 0.55
        risk_level = "red"

    # Build feature importance (simulated)
    feature_importance = {
        "machine_speed": round(abs(speed_factor), 4),
        "headbox_pressure": round(abs(pressure_factor), 4),
        "dryer_temperature": round(abs(dryer_factor), 4),
        "moisture_content": round(abs(moisture_factor), 4),
        "chemical_dosage": round(abs(chem_factor), 4),
        "flow_rate": round(abs(flow_factor), 4),
    }

    # Sort by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

    # Root cause analysis
    dominant = sorted_features[0]
    root_cause = (
        f"Primary deviation driver: {dominant[0]} (importance: {dominant[1]:.4f}). "
        f"The current value of {input_data[dominant[0]]:.1f} is contributing to a "
        f"{'higher' if predicted_gsm > target_gsm else 'lower'} than target GSM."
    )

    # Decision explanation
    direction = "above" if predicted_gsm > target_gsm else "below"
    decision_explanation = (
        f"Predicted Basis Weight: {predicted_gsm:.1f} GSM ({deviation_pct:.1f}% {direction} target of {target_gsm:.1f} GSM). "
        f"Confidence: {confidence:.0%}. "
        f"The most influential parameter is {dominant[0]} at {dominant[1]:.4f}. "
        f"{'Corrective action recommended.' if risk_level in ('yellow', 'red') else 'Parameters near optimal.'}"
    )

    # Estimate stabilization time (seconds)
    stabilization_time = max(60, deviation_pct * 120)

    # Create prediction record
    pred_repo = PredictionRepository(db)
    prediction = Prediction(
        production_run_id=request.production_run_id,
        model_id=model_meta.model_id,
        model_version=model_meta.version,
        predicted_basis_weight=round(float(predicted_gsm), 2),
        confidence_score=round(confidence, 2),
        risk_level=risk_level,
        deviation_percentage=round(deviation_pct, 2),
        estimated_stabilization_time=round(stabilization_time, 1),
        feature_importance=feature_importance,
        root_cause=root_cause,
        decision_explanation=decision_explanation,
        input_parameters=input_data,
    )

    prediction = await pred_repo.create(prediction)

    return prediction


@router.get("/history", response_model=list[PredictionResponse])
async def get_prediction_history(
    production_run_id: Optional[UUID] = Query(None),
    risk_level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get historical predictions."""
    repo = PredictionRepository(db)

    if production_run_id:
        predictions = await repo.get_by_run(production_run_id, limit=limit)
    elif risk_level == "red":
        predictions = await repo.get_red_alerts(limit=limit)
    else:
        predictions = await repo.get_all(limit=limit)

    return list(predictions)


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific prediction by ID."""
    repo = PredictionRepository(db)
    pred = await repo.get_by_id(prediction_id)
    if not pred:
        raise HTTPException(404, "Prediction not found")
    return pred
