"""GradeWise AI - Domain-specific repositories."""

from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Alert,
    GradeTransition,
    ModelMetadata,
    OperatorLog,
    PaperGrade,
    Prediction,
    ProductionRun,
    Recommendation,
    SensorReading,
    User,
)
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()


class PaperGradeRepository(BaseRepository[PaperGrade]):
    def __init__(self, session: AsyncSession):
        super().__init__(PaperGrade, session)

    async def get_by_gsm(self, gsm: float) -> Optional[PaperGrade]:
        result = await self.session.execute(
            select(PaperGrade).where(PaperGrade.gsm_target == gsm)
        )
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> Sequence[PaperGrade]:
        result = await self.session.execute(
            select(PaperGrade)
            .where(PaperGrade.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return result.scalars().all()


class ProductionRunRepository(BaseRepository[ProductionRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProductionRun, session)

    async def get_active_runs(self) -> Sequence[ProductionRun]:
        result = await self.session.execute(
            select(ProductionRun).where(
                ProductionRun.status.in_(["running", "transitioning", "stabilizing"])
            )
        )
        return result.scalars().all()

    async def get_runs_by_machine(self, machine_id: str, limit: int = 50) -> Sequence[ProductionRun]:
        result = await self.session.execute(
            select(ProductionRun)
            .where(ProductionRun.machine_id == machine_id)
            .order_by(desc(ProductionRun.started_at))
            .limit(limit)
        )
        return result.scalars().all()


class SensorReadingRepository(BaseRepository[SensorReading]):
    def __init__(self, session: AsyncSession):
        super().__init__(SensorReading, session)

    async def get_by_run(
        self, production_run_id: UUID, limit: int = 1000, offset: int = 0
    ) -> Sequence[SensorReading]:
        result = await self.session.execute(
            select(SensorReading)
            .where(SensorReading.production_run_id == production_run_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_latest_for_run(self, production_run_id: UUID) -> Optional[SensorReading]:
        result = await self.session.execute(
            select(SensorReading)
            .where(SensorReading.production_run_id == production_run_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_time_range(
        self,
        production_run_id: UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> Sequence[SensorReading]:
        result = await self.session.execute(
            select(SensorReading)
            .where(
                and_(
                    SensorReading.production_run_id == production_run_id,
                    SensorReading.timestamp >= start_time,
                    SensorReading.timestamp <= end_time,
                )
            )
            .order_by(SensorReading.timestamp)
        )
        return result.scalars().all()

    async def get_recent(self, production_run_id: UUID, limit: int = 50) -> Sequence[SensorReading]:
        """Get most recent readings for a production run."""
        result = await self.session.execute(
            select(SensorReading)
            .where(SensorReading.production_run_id == production_run_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())[::-1]  # Return in chronological order


class GradeTransitionRepository(BaseRepository[GradeTransition]):
    def __init__(self, session: AsyncSession):
        super().__init__(GradeTransition, session)

    async def search_transitions(
        self,
        from_grade_id: Optional[UUID] = None,
        to_grade_id: Optional[UUID] = None,
        success: Optional[bool] = None,
        limit: int = 20,
    ) -> Sequence[GradeTransition]:
        conditions = []
        if from_grade_id:
            conditions.append(GradeTransition.from_grade_id == from_grade_id)
        if to_grade_id:
            conditions.append(GradeTransition.to_grade_id == to_grade_id)
        if success is not None:
            conditions.append(GradeTransition.success == success)

        query = select(GradeTransition).order_by(desc(GradeTransition.created_at)).limit(limit)
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_similar_transitions(
        self, from_gsm: float, to_gsm: float, limit: int = 10
    ) -> list[GradeTransition]:
        """Find similar grade transitions by GSM values."""
        result = await self.session.execute(
            select(GradeTransition)
            .join(PaperGrade, GradeTransition.from_grade_id == PaperGrade.id)
            .where(
                and_(
                    func.abs(PaperGrade.gsm_target - from_gsm) < 5,
                )
            )
            .order_by(desc(GradeTransition.created_at))
            .limit(limit)
        )
        transitions = list(result.scalars().all())

        # Further filter by to_grade GSM - approximate second join
        result2 = await self.session.execute(
            select(GradeTransition)
            .join(PaperGrade, GradeTransition.to_grade_id == PaperGrade.id)
            .where(
                and_(
                    func.abs(PaperGrade.gsm_target - to_gsm) < 5,
                )
            )
            .order_by(desc(GradeTransition.created_at))
            .limit(limit)
        )
        transitions2 = list(result2.scalars().all())

        # Intersection of both
        ids1 = {t.id for t in transitions}
        return [t for t in transitions2 if t.id in ids1][:limit]


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: AsyncSession):
        super().__init__(Prediction, session)

    async def get_by_run(
        self, production_run_id: UUID, limit: int = 100
    ) -> Sequence[Prediction]:
        result = await self.session.execute(
            select(Prediction)
            .where(Prediction.production_run_id == production_run_id)
            .order_by(Prediction.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_latest_for_run(self, production_run_id: UUID) -> Optional[Prediction]:
        result = await self.session.execute(
            select(Prediction)
            .where(Prediction.production_run_id == production_run_id)
            .order_by(Prediction.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_red_alerts(self, limit: int = 50) -> Sequence[Prediction]:
        result = await self.session.execute(
            select(Prediction)
            .where(Prediction.risk_level == "red")
            .order_by(Prediction.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Recommendation, session)

    async def get_by_run(
        self, production_run_id: UUID, limit: int = 50
    ) -> Sequence[Recommendation]:
        result = await self.session.execute(
            select(Recommendation)
            .where(Recommendation.production_run_id == production_run_id)
            .order_by(Recommendation.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_pending(self, limit: int = 50) -> Sequence[Recommendation]:
        result = await self.session.execute(
            select(Recommendation)
            .where(Recommendation.status == "pending")
            .order_by(Recommendation.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


class AlertRepository(BaseRepository[Alert]):
    def __init__(self, session: AsyncSession):
        super().__init__(Alert, session)

    async def get_by_run(
        self, production_run_id: UUID, limit: int = 100
    ) -> Sequence[Alert]:
        result = await self.session.execute(
            select(Alert)
            .where(Alert.production_run_id == production_run_id)
            .order_by(Alert.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_unacknowledged(self, limit: int = 50) -> Sequence[Alert]:
        result = await self.session.execute(
            select(Alert)
            .where(Alert.is_acknowledged == False)  # noqa: E712
            .order_by(Alert.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_priority(
        self, priority: str, limit: int = 50
    ) -> Sequence[Alert]:
        result = await self.session.execute(
            select(Alert)
            .where(Alert.priority == priority)
            .order_by(Alert.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


class ModelMetadataRepository(BaseRepository[ModelMetadata]):
    def __init__(self, session: AsyncSession):
        super().__init__(ModelMetadata, session)

    async def get_active_model(self, model_type: str = "basis_weight") -> Optional[ModelMetadata]:
        result = await self.session.execute(
            select(ModelMetadata)
            .where(
                and_(
                    ModelMetadata.model_type == model_type,
                    ModelMetadata.is_active == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_model_id(self, model_id: str) -> Sequence[ModelMetadata]:
        result = await self.session.execute(
            select(ModelMetadata)
            .where(ModelMetadata.model_id == model_id)
            .order_by(ModelMetadata.version.desc())
        )
        return result.scalars().all()

    async def deactivate_all(self, model_type: str) -> None:
        """Deactivate all models of a given type."""
        models = await self.session.execute(
            select(ModelMetadata).where(
                and_(
                    ModelMetadata.model_type == model_type,
                    ModelMetadata.is_active == True,  # noqa: E712
                )
            )
        )
        for model in models.scalars().all():
            model.is_active = False
            self.session.add(model)
        await self.session.flush()


class OperatorLogRepository(BaseRepository[OperatorLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(OperatorLog, session)

    async def get_by_run(
        self, production_run_id: UUID, limit: int = 100
    ) -> Sequence[OperatorLog]:
        result = await self.session.execute(
            select(OperatorLog)
            .where(OperatorLog.production_run_id == production_run_id)
            .order_by(OperatorLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
