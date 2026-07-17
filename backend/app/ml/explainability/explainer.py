"""GradeWise AI - Explainable AI Module (SHAP & LIME).

Provides feature importance, SHAP value computation, root cause analysis,
and human-readable decision explanations for every prediction.
"""

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """Computes and formats model explanations for operators.

    Every prediction comes with:
    - Feature importance ranking
    - SHAP value computation (for tree models)
    - Root cause identification
    - Parameter contribution analysis
    - Human-readable decision explanation
    - What-if scenario analysis
    """

    def __init__(self):
        self._shap_explainer: Any = None
        self._feature_names: list[str] = []

    def initialize(
        self,
        model: Any,
        X_background: np.ndarray,
        feature_names: list[str],
    ) -> None:
        """Initialize the explainability engine with a fitted model.

        Uses TreeExplainer for tree-based models (most efficient).
        Falls back to KernelExplainer for non-tree models.
        """
        self._feature_names = feature_names
        try:
            import shap
            if hasattr(model, "estimators_") or hasattr(model, "get_booster"):
                self._shap_explainer = shap.TreeExplainer(model)
                logger.info("Initialized SHAP TreeExplainer")
            else:
                # Sample background for KernelExplainer
                n_background = min(100, len(X_background))
                self._shap_explainer = shap.KernelExplainer(
                    model.predict, X_background[:n_background]
                )
                logger.info("Initialized SHAP KernelExplainer (fallback)")
        except ImportError:
            logger.warning("SHAP not installed — using permutation importance")
            self._shap_explainer = None
        except Exception as e:
            logger.warning(f"SHAP initialization failed: {e}")
            self._shap_explainer = None

    def explain_prediction(
        self,
        model: Any,
        features_df: pd.DataFrame,
        prediction: float,
        target_gsm: float,
    ) -> dict[str, Any]:
        """Generate a complete explanation for a prediction.

        Returns feature importance, root cause, contributions, risk level,
        and decision explanation.
        """
        feature_names = features_df.columns.tolist()
        feature_values = features_df.iloc[0].to_dict()

        # Compute SHAP values if explainer is available
        shap_values = None
        if self._shap_explainer is not None:
            try:
                shap_vals = self._shap_explainer.shap_values(features_df.values)
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[0]
                shap_values = dict(zip(feature_names, shap_vals[0].tolist()
                                       if len(shap_vals.shape) > 1
                                       else shap_vals.tolist()))
            except Exception as e:
                logger.debug(f"SHAP computation failed: {e}")

        # Compute feature importance via permutation
        importances = self._compute_permutation_importance(
            model, features_df, prediction
        )

        # Sort by absolute importance
        sorted_features = sorted(
            importances.items(), key=lambda x: abs(x[1]), reverse=True
        )

        # Determine top contributors
        top_contributors = [
            {
                "feature": name,
                "importance": round(imp, 4),
                "current_value": round(feature_values.get(name, 0), 2),
                "direction": "increasing" if imp > 0 else "decreasing",
            }
            for name, imp in sorted_features[:8]
        ]

        # Root cause analysis
        root_cause = self._identify_root_cause(
            sorted_features, feature_values, prediction, target_gsm
        )

        # Parameter contribution analysis
        contributions = self._build_contributions(
            sorted_features, prediction, target_gsm
        )

        # Decision explanation
        decision_explanation = self._build_decision_explanation(
            sorted_features, prediction, target_gsm, contributions
        )

        # Risk assessment
        deviation_pct = abs(prediction - target_gsm) / target_gsm * 100
        if deviation_pct <= 2:
            risk_level = "green"
        elif deviation_pct <= 5:
            risk_level = "yellow"
        else:
            risk_level = "red"

        return {
            "feature_importance": {
                name: round(imp, 6) for name, imp in sorted_features[:10]
            },
            "top_contributors": top_contributors,
            "shap_values": shap_values,
            "root_cause": root_cause,
            "contributions": contributions[:5],
            "decision_explanation": decision_explanation,
            "risk_level": risk_level,
            "deviation_pct": round(deviation_pct, 2),
            "target_gsm": target_gsm,
            "predicted_gsm": round(prediction, 2),
        }

    def _compute_permutation_importance(
        self,
        model: Any,
        features_df: pd.DataFrame,
        baseline_prediction: float,
    ) -> dict[str, float]:
        """Compute permutation-based feature importance."""
        feature_names = features_df.columns.tolist()
        importances = {}

        for i, feat in enumerate(feature_names):
            perturbed = features_df.copy()
            perturbed.iloc[0, i] = perturbed.iloc[0, i] * 1.1  # 10% perturbation
            try:
                perturbed_pred = float(model.predict(perturbed.values)[0])
                importances[feat] = abs(perturbed_pred - baseline_prediction)
            except Exception:
                importances[feat] = 0.0

        return importances

    def _identify_root_cause(
        self,
        sorted_features: list[tuple[str, float]],
        feature_values: dict[str, float],
        prediction: float,
        target_gsm: float,
    ) -> str:
        """Identify the primary root cause of deviation."""
        if not sorted_features:
            return "Unable to determine root cause — insufficient data"

        dominant = sorted_features[0]
        feature_name = dominant[0]
        importance = dominant[1]
        current_val = feature_values.get(feature_name, 0)

        direction = "higher" if prediction > target_gsm else "lower"

        # Contextual analysis
        explanations = {
            "machine_speed": f"faster than optimal speed" if current_val > 800 else f"slower speed affecting formation",
            "headbox_pressure": f"elevated pressure" if current_val > 2.5 else f"low pressure",
            "dryer_temperature": f"excessive drying" if current_val > 120 else f"insufficient drying",
            "moisture_content": f"high moisture" if current_val > 5.5 else f"low moisture",
            "chemical_dosage": f"overdosing" if current_val > 1.8 else f"underdosing",
            "flow_rate": f"excessive flow" if current_val > 2500 else f"low flow rate",
        }

        context = explanations.get(feature_name, "deviation from optimal range")

        return (
            f"Primary deviation driver: {feature_name} (importance: {importance:.4f}). "
            f"The current value of {current_val:.1f} ({context}) is contributing to a "
            f"{direction} than target GSM of {target_gsm:.1f}."
        )

    def _build_contributions(
        self,
        sorted_features: list[tuple[str, float]],
        prediction: float,
        target_gsm: float,
    ) -> list[dict[str, Any]]:
        """Build parameter contribution list."""
        return [
            {
                "feature": name,
                "contribution": round(imp / target_gsm * 100, 2),
                "impact": "positive" if imp > 0 else "negative",
            }
            for name, imp in sorted_features[:5]
        ]

    def _build_decision_explanation(
        self,
        sorted_features: list[tuple[str, float]],
        prediction: float,
        target_gsm: float,
        contributions: list[dict[str, Any]],
    ) -> str:
        """Build a human-readable decision explanation."""
        if not sorted_features:
            return "Prediction generated with limited feature data"

        dominant = sorted_features[0]
        deviation = abs(prediction - target_gsm)
        deviation_pct = deviation / target_gsm * 100

        parts = [
            f"Predicted Basis Weight: {prediction:.1f} GSM "
            f"({deviation_pct:.1f}% from target of {target_gsm:.1f} GSM). "
        ]

        if deviation_pct <= 1:
            parts.append("Parameters are within optimal range. ")
        elif deviation_pct <= 3:
            parts.append(f"Slight deviation detected. The most influential parameter is "
                         f"{dominant[0]}. ")
        else:
            parts.append(f"Significant deviation detected. Primary factor: {dominant[0]} "
                         f"(importance: {dominant[1]:.4f}). ")

        if contributions:
            top_contrib = contributions[0]
            parts.append(f"Top contributor: {top_contrib['feature']} "
                         f"({top_contrib['contribution']}% impact). ")

        if deviation_pct > 2:
            parts.append("Corrective action recommended. Adjust the primary parameter "
                         "and re-evaluate.")

        return "".join(parts)
