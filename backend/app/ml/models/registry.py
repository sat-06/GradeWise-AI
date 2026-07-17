"""GradeWise AI - ML Model Registry & Training Pipeline.

Implements model training, hyperparameter optimization, versioning,
and model comparison for basis weight prediction.
"""

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

from app.ml.pipeline.feature_engineering import CORE_FEATURES, TARGET, FeatureEngineer


class ModelRegistry:
    """Manages ML model training, versioning, and selection."""

    def __init__(
        self,
        models_dir: str = "ml/models/saved",
        experiment_name: str = "basis_weight_prediction",
    ):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.experiment_name = experiment_name
        self.feature_engineer = FeatureEngineer()

    def _create_models(self) -> dict[str, Any]:
        """Create a dictionary of candidate models for comparison."""
        return {
            "random_forest": RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=3,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42,
            ),
        }

    def train_and_compare(
        self,
        df: pd.DataFrame,
        target_col: str = TARGET,
        n_splits: int = 5,
    ) -> dict[str, Any]:
        """Train all candidate models and select the best performer.

        Args:
            df: Training DataFrame with features and target
            target_col: Name of target column
            n_splits: Number of time-series cross-validation splits

        Returns:
            Dict with best model info, all metrics, and model artifacts
        """
        # Prepare features and target
        df_clean = df.dropna(subset=self.feature_engineer.features + [target_col])

        X = self.feature_engineer.fit_transform(df_clean, target_col)
        y = df_clean[target_col].values

        feature_names = self.feature_engineer.get_feature_names()

        tscv = TimeSeriesSplit(n_splits=n_splits)
        models = self._create_models()

        results = {}
        best_model = None
        best_score = -float("inf")

        for name, model in models.items():
            cv_scores = {"rmse": [], "mae": [], "r2": []}

            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]

                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)

                cv_scores["rmse"].append(np.sqrt(mean_squared_error(y_val, y_pred)))
                cv_scores["mae"].append(mean_absolute_error(y_val, y_pred))
                cv_scores["r2"].append(r2_score(y_val, y_pred))

            avg_rmse = np.mean(cv_scores["rmse"])
            avg_mae = np.mean(cv_scores["mae"])
            avg_r2 = np.mean(cv_scores["r2"])

            results[name] = {
                "rmse_mean": avg_rmse,
                "rmse_std": np.std(cv_scores["rmse"]),
                "mae_mean": avg_mae,
                "mae_std": np.std(cv_scores["mae"]),
                "r2_mean": avg_r2,
                "r2_std": np.std(cv_scores["r2"]),
            }

            if avg_r2 > best_score:
                best_score = avg_r2
                best_model = name

        # Train best model on full dataset
        final_model = models[best_model]
        final_model.fit(X, y)

        # Save model
        model_id = f"bw_predictor_{uuid.uuid4().hex[:8]}"
        version = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        model_dir = self.models_dir / model_id / version
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / "model.joblib"
        scaler_path = model_dir / "scaler.joblib"
        metadata_path = model_dir / "metadata.json"

        joblib.dump(final_model, model_path)
        joblib.dump(self.feature_engineer.scaler, scaler_path)

        metadata = {
            "model_id": model_id,
            "model_type": best_model,
            "version": version,
            "trained_at": datetime.now(UTC).isoformat(),
            "training_data_size": len(df_clean),
            "hyperparameters": final_model.get_params(),
            "metrics": results[best_model],
            "feature_names": feature_names,
            "model_path": str(model_path),
            "experiment_name": self.experiment_name,
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        return {
            "model_id": model_id,
            "best_model_type": best_model,
            "version": version,
            "metrics": results[best_model],
            "all_results": results,
            "model_path": str(model_path),
            "metadata_path": str(metadata_path),
            "feature_names": feature_names,
        }

    def load_model(self, model_id: str, version: str) -> tuple[Any, Any]:
        """Load a saved model and scaler."""
        model_path = self.models_dir / model_id / version / "model.joblib"
        scaler_path = self.models_dir / model_id / version / "scaler.joblib"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path) if scaler_path.exists() else None

        return model, scaler

    def load_latest_model(self, model_id: str) -> tuple[Any, Any, dict]:
        """Load the latest version of a model."""
        model_base = self.models_dir / model_id
        if not model_base.exists():
            raise FileNotFoundError(f"Model not found: {model_id}")

        versions = sorted(
            [d.name for d in model_base.iterdir() if d.is_dir()],
            reverse=True,
        )
        if not versions:
            raise FileNotFoundError(f"No versions found for model: {model_id}")

        latest = versions[0]
        model, scaler = self.load_model(model_id, latest)

        metadata_path = model_base / latest / "metadata.json"
        with open(metadata_path) as f:
            metadata = json.load(f)

        return model, scaler, metadata

    def predict(
        self,
        model: Any,
        scaler: Any,
        features_df: pd.DataFrame,
    ) -> np.ndarray:
        """Make predictions using a loaded model."""
        # Apply the same feature engineering
        X = self.feature_engineer.transform(features_df)
        return model.predict(X)

    def predict_single(
        self,
        model: Any,
        feature_dict: dict[str, float],
    ) -> float:
        """Make a single prediction from a feature dictionary."""
        df = pd.DataFrame([feature_dict])

        # Fill missing features with defaults
        for feat in self.feature_engineer.features:
            if feat not in df.columns:
                df[feat] = 0.0

        X = self.feature_engineer.transform(df)
        return float(model.predict(X)[0])
