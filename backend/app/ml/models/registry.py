"""GradeWise AI - ML Model Registry & Training Pipeline.

Implements model training, hyperparameter optimization, versioning,
and model comparison for basis weight prediction.

Supports: Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost
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


# Try importing optional ML libraries — gracefully degrade if unavailable
def _import_xgboost():
    try:
        import xgboost as xgb
        return xgb.XGBRegressor
    except ImportError:
        return None

def _import_lightgbm():
    try:
        import lightgbm as lgb
        return lgb.LGBMRegressor
    except ImportError:
        return None

def _import_catboost():
    try:
        import catboost as cb
        return cb.CatBoostRegressor
    except ImportError:
        return None


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
        self.feature_engineer = FeatureEngineer(
            use_rolling_features=True,
            use_lag_features=True,
            use_interaction_features=True,
            use_transition_features=True,
        )

    def _create_models(self) -> dict[str, Any]:
        """Create a dictionary of candidate models for comparison.

        Returns all available models. Libraries that are not installed
        are silently skipped so the pipeline doesn't crash.
        """
        models = {
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

        # XGBoost
        XGB = _import_xgboost()
        if XGB:
            models["xgboost"] = XGB(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbosity=0,
            )

        # LightGBM
        LGB = _import_lightgbm()
        if LGB:
            models["lightgbm"] = LGB(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            )

        # CatBoost
        CB = _import_catboost()
        if CB:
            models["catboost"] = CB(
                iterations=200,
                depth=6,
                learning_rate=0.05,
                random_seed=42,
                thread_count=-1,
                verbose=False,
            )

        return models

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
        features_existing = [f for f in self.feature_engineer.features if f in df.columns]
        self.feature_engineer.features = features_existing
        df_clean = df.dropna(subset=features_existing + [target_col])

        X = self.feature_engineer.fit_transform(df_clean, target_col)
        y = df_clean[target_col].values

        feature_names = self.feature_engineer.get_feature_names()

        tscv = TimeSeriesSplit(n_splits=min(n_splits, len(X) - 1))
        models = self._create_models()

        results = {}
        best_model_name = None
        best_score = -float("inf")

        for name, model in models.items():
            cv_scores = {"rmse": [], "mae": [], "r2": []}

            try:
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
                    best_model_name = name

            except Exception as e:
                print(f"  ⚠ {name} training failed: {e}")
                continue

        if best_model_name is None:
            raise RuntimeError("No models trained successfully. Check your ML dependencies.")

        # Train best model on full dataset
        final_model = models[best_model_name]
        final_model.fit(X, y)

        # Save model
        model_id = f"bw_predictor_{uuid.uuid4().hex[:8]}"
        version = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        model_dir = self.models_dir / model_id / version
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / "model.joblib"
        scaler_path = model_dir / "scaler.joblib"
        preprocessor_path = model_dir / "preprocessor.joblib"
        metadata_path = model_dir / "metadata.json"

        joblib.dump(final_model, model_path)
        joblib.dump(self.feature_engineer.scaler, scaler_path)
        # Save the entire feature engineer for inference
        joblib.dump(self.feature_engineer, preprocessor_path)

        metadata = {
            "model_id": model_id,
            "model_type": best_model_name,
            "version": version,
            "trained_at": datetime.now(UTC).isoformat(),
            "training_data_size": len(df_clean),
            "hyperparameters": {k: str(v) for k, v in final_model.get_params().items()},
            "metrics": results[best_model_name],
            "feature_names": feature_names,
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
            "preprocessor_path": str(preprocessor_path),
            "experiment_name": self.experiment_name,
            "all_results": results,
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        return {
            "model_id": model_id,
            "best_model_type": best_model_name,
            "version": version,
            "metrics": results[best_model_name],
            "all_results": results,
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
            "preprocessor_path": str(preprocessor_path),
            "metadata_path": str(metadata_path),
            "feature_names": feature_names,
        }

    def load_model(self, model_id: str, version: str) -> tuple[Any, Any, Any]:
        """Load a saved model, scaler, and preprocessor."""
        model_path = self.models_dir / model_id / version / "model.joblib"
        scaler_path = self.models_dir / model_id / version / "scaler.joblib"
        preprocessor_path = self.models_dir / model_id / version / "preprocessor.joblib"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path) if scaler_path.exists() else None
        preprocessor = joblib.load(preprocessor_path) if preprocessor_path.exists() else None

        return model, scaler, preprocessor

    def load_latest_model(self, model_id: str) -> tuple[Any, Any, dict]:
        """Load the latest version of a model with its metadata."""
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
        model, scaler, preprocessor = self.load_model(model_id, latest)

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

    def predict_with_confidence(
        self,
        model: Any,
        features_df: pd.DataFrame,
        confidence: float = 0.95,
    ) -> dict[str, Any]:
        """Make predictions with confidence intervals.

        Uses residual standard deviation from training to estimate
        prediction intervals when the model supports it.

        Returns:
            Dict with prediction, lower bound, upper bound, and confidence level.
        """
        X = self.feature_engineer.transform(features_df)
        prediction = float(model.predict(X)[0])

        # Estimate prediction interval from training metrics
        # Load metadata for residual std estimate
        try:
            metadata = self._load_latest_metadata()
            rmse = metadata.get("metrics", {}).get("rmse_mean", 1.0)
        except Exception:
            rmse = 1.5  # sensible default

        # z-score for confidence level (95% -> 1.96, 90% -> 1.645)
        if confidence >= 0.99:
            z = 2.576
        elif confidence >= 0.95:
            z = 1.96
        elif confidence >= 0.90:
            z = 1.645
        else:
            z = 1.0

        margin = z * rmse
        return {
            "prediction": round(prediction, 2),
            "lower_bound": round(prediction - margin, 2),
            "upper_bound": round(prediction + margin, 2),
            "confidence_level": confidence,
            "rmse_estimate": round(rmse, 4),
        }

    def _load_latest_metadata(self) -> dict:
        """Load metadata from the latest saved model."""
        versions = sorted(self.models_dir.iterdir(), key=os.path.getmtime, reverse=True)
        for v in versions:
            if v.is_dir():
                for sub in sorted(v.iterdir(), reverse=True):
                    meta = sub / "metadata.json"
                    if meta.exists():
                        with open(meta) as f:
                            return json.load(f)
        return {}
