"""GradeWise AI - ORM Models for all domain entities."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class User(Base):
    """Platform user (operator, engineer, admin)."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("operator", "engineer", "supervisor", "admin", name="user_role"),
        default="operator",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PaperGrade(Base):
    """Paper grade reference data (e.g., 70 GSM, 120 GSM)."""

    __tablename__ = "paper_grades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    gsm_target: Mapped[float] = mapped_column(Float, nullable=False)
    gsm_tolerance_min: Mapped[float] = mapped_column(Float, nullable=False)
    gsm_tolerance_max: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProductionRun(Base):
    """A continuous production run on a paper machine."""

    __tablename__ = "production_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    current_grade_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("paper_grades.id"), nullable=True)
    target_grade_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("paper_grades.id"), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("running", "transitioning", "stabilizing", "stopped", "maintenance", name="machine_status"),
        default="running",
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    current_grade = relationship("PaperGrade", foreign_keys=[current_grade_id])
    target_grade = relationship("PaperGrade", foreign_keys=[target_grade_id])


class SensorReading(Base):
    """Individual sensor reading from the production line."""

    __tablename__ = "sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_runs.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Key process variables
    basis_weight: Mapped[float] = mapped_column(Float, nullable=False)
    machine_speed: Mapped[float] = mapped_column(Float, nullable=False)
    headbox_pressure: Mapped[float] = mapped_column(Float, nullable=False)
    dryer_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    moisture_content: Mapped[float] = mapped_column(Float, nullable=False)
    chemical_dosage: Mapped[float] = mapped_column(Float, nullable=False)
    flow_rate: Mapped[float] = mapped_column(Float, nullable=False)
    vacuum_pressure: Mapped[float] = mapped_column(Float, nullable=True)
    wire_tension: Mapped[float] = mapped_column(Float, nullable=True)
    press_load: Mapped[float] = mapped_column(Float, nullable=True)
    stock_consistency: Mapped[float] = mapped_column(Float, nullable=True)
    ambient_temperature: Mapped[float] = mapped_column(Float, nullable=True)
    ambient_humidity: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_run = relationship("ProductionRun")


class GradeTransition(Base):
    """Record of a grade transition event between two paper grades."""

    __tablename__ = "grade_transitions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_runs.id"), nullable=False, index=True)
    from_grade_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("paper_grades.id"), nullable=False)
    to_grade_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("paper_grades.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    stabilization_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    waste_generated_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    parameter_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    operator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    from_grade = relationship("PaperGrade", foreign_keys=[from_grade_id])
    to_grade = relationship("PaperGrade", foreign_keys=[to_grade_id])
    production_run = relationship("ProductionRun")


class Prediction(Base):
    """AI prediction record."""

    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_runs.id"), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    predicted_basis_weight: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(
        Enum("green", "yellow", "red", name="risk_level"), nullable=False
    )
    deviation_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_stabilization_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Explainability
    shap_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Input snapshot
    input_parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_run = relationship("ProductionRun")


class Recommendation(Base):
    """AI-generated machine setting recommendation."""

    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id"), nullable=True)
    production_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_runs.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recommended_settings: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_basis_weight: Mapped[float] = mapped_column(Float, nullable=False)
    expected_improvement: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)

    # Operator feedback
    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "rejected", "modified", "applied", name="recommendation_status"),
        default="pending",
    )
    operator_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    operator_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    modified_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prediction = relationship("Prediction")
    production_run = relationship("ProductionRun")


class Alert(Base):
    """Intelligent alert with priority, reason, and recommended action."""

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_runs.id"), nullable=False, index=True)
    prediction_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("predictions.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    priority: Mapped[str] = mapped_column(
        Enum("green", "yellow", "red", name="alert_priority"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    expected_impact: Mapped[str] = mapped_column(Text, nullable=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_run = relationship("ProductionRun")


class ModelMetadata(Base):
    """ML model registry and versioning."""

    __tablename__ = "model_metadata"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    training_data_size: Mapped[int] = mapped_column(Integer, nullable=False)
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    feature_names: Mapped[list] = mapped_column(JSON, nullable=False)
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)
    shap_explainer_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rmse: Mapped[float] = mapped_column(Float, nullable=False)
    mae: Mapped[float] = mapped_column(Float, nullable=False)
    r2_score: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("model_id", "version", name="uq_model_version"),
    )


class OperatorLog(Base):
    """Operator actions and manual interventions log."""

    __tablename__ = "operator_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_runs.id"), nullable=False, index=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    action_type: Mapped[str] = mapped_column(
        Enum(
            "parameter_change",
            "grade_change_initiated",
            "recommendation_accepted",
            "recommendation_rejected",
            "recommendation_modified",
            "alert_acknowledged",
            "manual_override",
            "comment",
            name="operator_action_type",
        ),
        nullable=False,
    )
    details: Mapped[dict] = mapped_column(JSON, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
