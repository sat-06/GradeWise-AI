"""GradeWise AI - Feature Engineering Pipeline.

Handles feature extraction, selection, and transformation for the ML models.
Designed to work with both synthetic and real plant data through a clean interface.
"""

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler


# Feature definitions — extend these when adding new data sources
CORE_FEATURES = [
    "machine_speed",
    "headbox_pressure",
    "dryer_temperature",
    "moisture_content",
    "chemical_dosage",
    "flow_rate",
]

EXTENDED_FEATURES = [
    "vacuum_pressure",
    "wire_tension",
    "press_load",
    "stock_consistency",
    "ambient_temperature",
    "ambient_humidity",
]

ALL_FEATURES = CORE_FEATURES + EXTENDED_FEATURES

TARGET = "basis_weight"


class FeatureEngineer:
    """Feature engineering pipeline for paper manufacturing data.

    This class handles:
    - Feature extraction from raw sensor data
    - Rolling window statistics (trend features)
    - Lag features for time-series awareness
    - Feature scaling and normalization
    - Feature selection and importance ranking
    """

    def __init__(
        self,
        features: Optional[list[str]] = None,
        use_rolling_features: bool = True,
        use_lag_features: bool = True,
        use_interaction_features: bool = True,
        window_sizes: list[int] = [5, 10, 30],
        scaler_type: str = "robust",
    ):
        self.features = features or CORE_FEATURES
        self.use_rolling_features = use_rolling_features
        self.use_lag_features = use_lag_features
        self.use_interaction_features = use_interaction_features
        self.window_sizes = window_sizes
        self.scaler_type = scaler_type

        self.scaler: StandardScaler | RobustScaler
        if scaler_type == "robust":
            self.scaler = RobustScaler()
        else:
            self.scaler = StandardScaler()

        self._fitted = False
        self.feature_names_: list[str] = []

    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling mean and std features for core parameters."""
        result = df.copy()
        for feature in self.features:
            for window in self.window_sizes:
                if len(result) >= window:
                    result[f"{feature}_rolling_mean_{window}"] = (
                        result[feature].rolling(window=window, min_periods=1).mean()
                    )
                    result[f"{feature}_rolling_std_{window}"] = (
                        result[feature].rolling(window=window, min_periods=1).std().fillna(0)
                    )
        return result

    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lag features (previous values) for core parameters."""
        result = df.copy()
        for feature in self.features:
            for lag in [1, 2, 5]:
                result[f"{feature}_lag_{lag}"] = result[feature].shift(lag).fillna(method="bfill")  # type: ignore[call-arg]
        return result

    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features between key parameter pairs."""
        result = df.copy()
        key_pairs = [
            ("machine_speed", "flow_rate"),
            ("dryer_temperature", "moisture_content"),
            ("headbox_pressure", "flow_rate"),
            ("chemical_dosage", "flow_rate"),
        ]
        for f1, f2 in key_pairs:
            if f1 in result.columns and f2 in result.columns:
                result[f"interaction_{f1}_{f2}"] = result[f1] * result[f2]
        return result

    def _add_derivative_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rate-of-change features."""
        result = df.copy()
        for feature in self.features:
            result[f"{feature}_delta"] = result[feature].diff().fillna(0)
        return result

    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> "FeatureEngineer":
        """Fit the feature engineering pipeline on training data."""
        processed = df.copy()

        if self.use_rolling_features:
            processed = self._add_rolling_features(processed)

        if self.use_lag_features:
            processed = self._add_lag_features(processed)

        if self.use_interaction_features:
            processed = self._add_interaction_features(processed)

        processed = self._add_derivative_features(processed)

        # Exclude non-feature columns
        exclude_cols = {
            "timestamp", "basis_weight", "gsm_target", "grade_name",
            "from_grade", "to_grade", "from_gsm", "to_gsm",
            "transition_progress", "is_stabilized", "target_gsm",
        }
        feature_cols = [
            col for col in processed.columns
            if col not in exclude_cols and processed[col].dtype in [np.float64, np.float32, np.int64, np.int32]
        ]

        # Fit scaler on features
        self.scaler.fit(processed[feature_cols])
        self.feature_names_ = feature_cols
        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform raw data into model-ready features."""
        if not self._fitted:
            raise RuntimeError("FeatureEngineer must be fitted before transform.")

        processed = df.copy()

        if self.use_rolling_features:
            processed = self._add_rolling_features(processed)

        if self.use_lag_features:
            processed = self._add_lag_features(processed)

        if self.use_interaction_features:
            processed = self._add_interaction_features(processed)

        processed = self._add_derivative_features(processed)

        # Ensure all feature columns exist
        for col in self.feature_names_:
            if col not in processed.columns:
                processed[col] = 0.0

        return self.scaler.transform(processed[self.feature_names_])

    def fit_transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(df, target_col)
        return self.transform(df)

    def get_feature_names(self) -> list[str]:
        """Return the list of engineered feature names."""
        return self.feature_names_

    def get_original_feature_names(self) -> list[str]:
        """Return the original (non-engineered) feature names."""
        return [f for f in self.feature_names_
                if not any(f.startswith(p + "_") for p in self.features
                          if f != p and not f.startswith("interaction_"))]
