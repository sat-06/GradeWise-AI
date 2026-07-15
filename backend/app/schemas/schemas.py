"""GradeWise AI - Pydantic Schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)
    role: str = Field(default="operator", pattern="^(operator|engineer|supervisor|admin)$")


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Paper Grade ───────────────────────────────────────

class PaperGradeCreate(BaseModel):
    name: str
    gsm_target: float
    gsm_tolerance_min: float
    gsm_tolerance_max: float
    description: Optional[str] = None


class PaperGradeResponse(BaseModel):
    id: UUID
    name: str
    gsm_target: float
    gsm_tolerance_min: float
    gsm_tolerance_max: float
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Production Run ────────────────────────────────────

class ProductionRunCreate(BaseModel):
    machine_id: str
    current_grade_id: Optional[UUID] = None
    target_grade_id: Optional[UUID] = None
    status: str = "running"


class ProductionRunResponse(BaseModel):
    id: UUID
    machine_id: str
    current_grade_id: Optional[UUID] = None
    target_grade_id: Optional[UUID] = None
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Sensor Reading ────────────────────────────────────

class SensorReadingCreate(BaseModel):
    production_run_id: UUID
    timestamp: datetime
    basis_weight: float
    machine_speed: float
    headbox_pressure: float
    dryer_temperature: float
    moisture_content: float
    chemical_dosage: float
    flow_rate: float
    vacuum_pressure: Optional[float] = None
    wire_tension: Optional[float] = None
    press_load: Optional[float] = None
    stock_consistency: Optional[float] = None
    ambient_temperature: Optional[float] = None
    ambient_humidity: Optional[float] = None


class SensorReadingResponse(BaseModel):
    id: UUID
    production_run_id: UUID
    timestamp: datetime
    basis_weight: float
    machine_speed: float
    headbox_pressure: float
    dryer_temperature: float
    moisture_content: float
    chemical_dosage: float
    flow_rate: float
    vacuum_pressure: Optional[float] = None
    wire_tension: Optional[float] = None
    press_load: Optional[float] = None
    stock_consistency: Optional[float] = None
    ambient_temperature: Optional[float] = None
    ambient_humidity: Optional[float] = None

    model_config = {"from_attributes": True}


# ── Grade Transition ──────────────────────────────────

class GradeTransitionCreate(BaseModel):
    production_run_id: UUID
    from_grade_id: UUID
    to_grade_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    parameter_settings: Optional[dict] = None
    operator_notes: Optional[str] = None


class GradeTransitionResponse(BaseModel):
    id: UUID
    production_run_id: UUID
    from_grade_id: UUID
    to_grade_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    stabilization_time_seconds: Optional[float] = None
    success: Optional[bool] = None
    waste_generated_kg: Optional[float] = None
    parameter_settings: Optional[dict] = None
    operator_notes: Optional[str] = None
    lessons_learned: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Prediction ────────────────────────────────────────

class PredictionRequest(BaseModel):
    production_run_id: UUID
    machine_speed: float
    headbox_pressure: float
    dryer_temperature: float
    moisture_content: float
    chemical_dosage: float
    flow_rate: float
    vacuum_pressure: Optional[float] = None
    wire_tension: Optional[float] = None
    press_load: Optional[float] = None
    stock_consistency: Optional[float] = None
    from_grade_gsm: Optional[float] = None
    to_grade_gsm: Optional[float] = None


class PredictionResponse(BaseModel):
    id: UUID
    production_run_id: UUID
    model_id: str
    model_version: str
    timestamp: datetime
    predicted_basis_weight: float
    confidence_score: float
    risk_level: str
    deviation_percentage: Optional[float] = None
    estimated_stabilization_time: Optional[float] = None
    shap_values: Optional[dict] = None
    feature_importance: Optional[dict] = None
    root_cause: Optional[str] = None
    decision_explanation: Optional[str] = None
    input_parameters: Optional[dict] = None

    model_config = {"from_attributes": True}


# ── Recommendation ────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: UUID
    prediction_id: Optional[UUID] = None
    production_run_id: UUID
    timestamp: datetime
    recommended_settings: dict
    expected_basis_weight: float
    expected_improvement: dict
    confidence: float
    reasoning: str
    status: str
    operator_feedback: Optional[str] = None

    model_config = {"from_attributes": True}


class OperatorFeedback(BaseModel):
    action: str = Field(pattern="^(accept|reject|modify)$")
    comments: Optional[str] = None
    modified_settings: Optional[dict] = None


# ── Alert ─────────────────────────────────────────────

class AlertResponse(BaseModel):
    id: UUID
    production_run_id: UUID
    timestamp: datetime
    priority: str
    title: str
    message: str
    reason: str
    recommended_action: str
    expected_impact: str
    is_acknowledged: bool
    is_resolved: bool

    model_config = {"from_attributes": True}


# ── What-If Simulation ────────────────────────────────

class WhatIfRequest(BaseModel):
    production_run_id: UUID
    machine_speed: float
    headbox_pressure: float
    dryer_temperature: float
    moisture_content: float
    chemical_dosage: float
    flow_rate: float


class WhatIfResponse(BaseModel):
    predicted_basis_weight: float
    risk_level: str
    confidence: float
    deviation_from_target: float
    estimated_waste_reduction: float
    production_impact: str
    parameter_changes: dict


# ── KPI / Analytics ───────────────────────────────────

class KPIData(BaseModel):
    estimated_waste_reduced_kg: float
    paper_saved_kg: float
    production_efficiency: float
    average_stabilization_time: float
    operator_acceptance_rate: float
    recommendation_success_rate: float
    total_predictions: int
    total_recommendations: int
    total_alerts: int
    average_confidence: float


# ── Search ───────────────────────────────────────────

class TransitionSearchRequest(BaseModel):
    from_gsm: Optional[float] = None
    to_gsm: Optional[float] = None
    success: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)


# ── Paginated Response ───────────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
