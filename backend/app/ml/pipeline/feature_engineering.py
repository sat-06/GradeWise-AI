"""GradeWise AI - Feature Engineering Pipeline.

Handles feature extraction, selection, and transformation for the ML models.
Designed to work with both synthetic and real plant data through a clean interface.

Includes:
- Rolling statistics (mean, std, trend)
- Lag features for time-series awareness
- Interaction features (moisture×GSM, dryer temp, machine speed, pressure×flow)
- Grade transition features (gsm deviation rate, transition progress, time since start)
- Actuator response delay features
- Machine-specific calibration features
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
    - Interaction features for cross-variable effects
    - Grade transition features
    - Feature scaling and normalization
    - Feature selection and importance ranking
    """

    def __init__(
        self,
        features: Optional[list[str]] = None,
        use_rolling_features: bool = True,
        use_lag_features: bool = True,
        use_interaction_features: bool = True,
        use_transition_features: bool = True,
        window_sizes: list[int] = [5, 10, 30],
        scaler_type: str = "robust",
    ):
        self.features = features or CORE_FEATURES
        self.use_rolling_features = use_rolling_features
        self.use_lag_features = use_lag_features
        self.use_interaction_features = use_interaction_features
        self.use_transition_features = use_transition_features
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
        """Add rolling mean, std, and trend/slope features for core parameters."""
        result = df.copy()
        for feature in self.features:
            if feature not in result.columns:
                continue
            for window in self.window_sizes:
                if len(result) >= window:
                    roll = result[feature].rolling(window=window, min_periods=1)
                    result[f"{feature}_rolling_mean_{window}"] = roll.mean()
                    result[f"{feature}_rolling_std_{window}"] = roll.std().fillna(0)
                    # Rolling trend (linear slope approximation)
                    if window >= 5:
                        result[f"{feature}_rolling_trend_{window}"] = (
                            result[f"{feature}_rolling_mean_{window}"]
                            .diff(periods=max(1, window // 2))
                            .fillna(0)
                        )
        return result

    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lag features (previous values) for core parameters."""
        result = df.copy()
        for feature in self.features:
            if feature not in result.columns:
                continue
            for lag in [1, 2, 5]:
                result[f"{feature}_lag_{lag}"] = result[feature].shift(lag)
                # Forward-fill for first rows that have no lag
                result[f"{feature}_lag_{lag}"] = result[f"{feature}_lag_{lag}"].fillna(
                    result[feature]
                )
        return result

    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features between key parameter pairs.

        Includes:
        - Moisture × GSM interaction (critical for paper quality)
        - Dryer temperature interaction with moisture and speed
        - Machine speed interaction with flow rate and tension
        - Pressure × Flow interaction (hydraulic coupling)
        """
        result = df.copy()

        # Core interaction pairs
        key_pairs = [
            ("machine_speed", "flow_rate"),
            ("dryer_temperature", "moisture_content"),
            ("headbox_pressure", "flow_rate"),
            ("chemical_dosage", "flow_rate"),
            ("machine_speed", "wire_tension"),
            ("dryer_temperature", "machine_speed"),
        ]
        for f1, f2 in key_pairs:
            if f1 in result.columns and f2 in result.columns:
                result[f"interaction_{f1}_{f2}"] = result[f1] * result[f2]

        # Moisture × GSM if available
        if "moisture_content" in result.columns and "basis_weight" in result.columns:
            result["interaction_moisture_gsm"] = (
                result["moisture_content"] * result["basis_weight"]
            )

        # Pressure × Flow (hydraulic coupling)
        if "headbox_pressure" in result.columns and "flow_rate" in result.columns:
            result["interaction_pressure_flow"] = (
                result["headbox_pressure"] * result["flow_rate"]
            )

        return result

    def _add_transition_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add grade transition-specific features.

        - GSM Deviation Rate: how fast GSM is changing
        - Previous GSM: most recent stable GSM value
        - Grade Difference: absolute difference between current and target
        - Transition Progress Percentage
        - Time Since Transition Started
        """
        result = df.copy()

        # GSM deviation rate (using 'basis_weight' column)
        if "basis_weight" in result.columns:
            result["gsm_deviation_rate"] = result["basis_weight"].diff().fillna(0)

        # Previous GSM (lag-1)
        if "basis_weight" in result.columns:
            result["previous_gsm"] = result["basis_weight"].shift(1).fillna(
                result["basis_weight"]
            )

        # Grade difference if target is available
        if "basis_weight" in result.columns and "gsm_target" in result.columns:
            result["grade_difference"] = (
                result["basis_weight"] - result["gsm_target"]
            ).abs()
            # Transition progress: how close to target (0-100%)
            max_dev = result["grade_difference"].max() or 1.0
            result["transition_progress_pct"] = (
                1.0 - result["grade_difference"] / max_dev
            ) * 100

        # Time since transition started (if timestamps available)
        if "timestamp" in result.columns:
            try:
                result["timestamp_dt"] = pd.to_datetime(result["timestamp"])
                result["time_since_start_sec"] = (
                    (result["timestamp_dt"] - result["timestamp_dt"].iloc[0])
                    .dt.total_seconds()
                    .fillna(0)
                )
                result = result.drop(columns=["timestamp_dt"])
            except Exception:
                result["time_since_start_sec"] = np.arange(len(result))

        return result

    def _add_derivative_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rate-of-change and actuator response features."""
        result = df.copy()

        # Rate of change (delta) for each feature
        for feature in self.features:
            if feature in result.columns:
                result[f"{feature}_delta"] = result[feature].diff().fillna(0)
                # Actuator response delay — 2nd derivative (acceleration of change)
                if f"{feature}_delta" in result.columns:
                    result[f"{feature}_accel"] = (
                        result[f"{feature}_delta"].diff().fillna(0)
                    )

        # Machine-specific calibration features (normalized ratios)
        if "machine_speed" in result.columns and "flow_rate" in result.columns:
            result["calibration_speed_flow_ratio"] = (
                result["machine_speed"] / result["flow_rate"].replace(0, np.nan)
            ).fillna(0)

        if "dryer_temperature" in result.columns and "machine_speed" in result.columns:
            result["calibration_dryer_speed_ratio"] = (
                result["dryer_temperature"] / result["machine_speed"].replace(0, np.nan)
            ).fillna(0)

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
        if self.use_transition_features:
            processed = self._add_transition_features(processed)

        processed = self._add_derivative_features(processed)

        # Exclude non-feature columns
        exclude_cols = {
            "timestamp", "basis_weight", "gsm_target", "grade_name",
            "from_grade", "to_grade", "from_gsm", "to_gsm",
            "transition_progress", "is_stabilized", "target_gsm",
            "timestamp_dt",
        }
        feature_cols = [
            col for col in processed.columns
            if col not in exclude_cols
            and processed[col].dtype in [np.float64, np.float32, np.int64, np.int32, np.int16]
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
        if self.use_transition_features:
            processed = self._add_transition_features(processed)

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
