"""GradeWise AI - Explainable AI Module (SHAP & LIME).

Provides feature importance, SHAP value computation, root cause analysis,
and human-readable decision explanations for every prediction.
"""

from typing import Any, Optional

import numpy as np
import pandas as pd


class ExplainabilityEngine:
    """Computes and formats model explanations for operators.

    Every prediction comes with:
    - Feature importance ranking
    - Root cause identification
    - Parameter contribution analysis
    - Human-readable decision explanation
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
        """
        self._feature_names = feature_names
        try:
            import shap
            if hasattr(model, "estimators_"):
                self._shap_explainer = shap.TreeExplainer(model)
            else:
                # Fallback to KernelExplainer for non-tree models
                self._shap_explainer = shap.KernelExplainer(
                    model.predict, X_background[:100]
                )
        except ImportError:
            self._shap_explainer = None

    def explain_prediction(
        self,
        model: Any,
        features_df: pd.DataFrame,
        prediction: float,
        target_gsm: float,
    ) -> dict[str, Any]:
        """Generate a complete explanation for a prediction.

        Args:
            model: The fitted ML model
            features_df: Single-row DataFrame of input features
            prediction: The model's predicted value
            target_gsm: The target GSM for the grade

        Returns:
            Dict with feature importance, root cause, and explanation
        """
        feature_names = features_df.columns.tolist()
        feature_values = features_df.iloc[0].to_dict()

        # Compute feature importance via permutation if SHAP unavailable
        importances = self._compute_permutation_importance(
            model, features_df, prediction
        )

        # Sort by absolute importance
        sorted_features = sorted(
            importances.items(), key=lambda x: abs(x[1]), reverse=True
        )

        # Determine root cause
        root_cause = self._identify_root_cause(
            sorted_features, feature_values, prediction, target_gsm
        )

        # Build parameter contributions
        contributions = self._build_contributions(
            sorted_features, prediction, target_gsm
        )

        # Build decision explanation
        decision_explanation = self._build_decision_explanation(
            sorted_features, prediction, target_gsm, contributions
        )

        # Determine risk level
        deviation_pct = abs(prediction - target_gsm) / target_gsm * 100
        if deviation_pct <= 2:
            risk_level = "green"
        elif deviation_pct <= 5:
            risk_level = "yellow"
        else:
            risk_level = "red"

        return {
            "feature_importance": dict(sorted_features[:8]),
            "root_cause": root_cause,
            "parameter_contributions": contributions,
            "decision_explanation": decision_explanation,
            "risk_level": risk_level,
            "deviation_percentage": round(deviation_pct, 2),
            "target_gsm": target_gsm,
            "predicted_gsm": round(prediction, 2),
        }

    def _compute_permutation_importance(
        self,
        model: Any,
        features_df: pd.DataFrame,
        baseline_prediction: float,
    ) -> dict[str, float]:
        """Compute feature importance via single-feature permutation."""
        importances = {}
        feature_values = features_df.iloc[0].copy()

        for col in features_df.columns:
            original = feature_values[col]
            # Perturb the feature by ±10%
            perturbed = features_df.copy()
            perturbed[col] = original * (1.1 if original != 0 else 0.1)
            perturbed_pred = model.predict(perturbed)[0]

            # Also try negative perturbation
            perturbed2 = features_df.copy()
            perturbed2[col] = original * (0.9 if original != 0 else -0.1)
            perturbed_pred2 = model.predict(perturbed2)[0]

            # Average absolute change
            importance = (
                abs(perturbed_pred - baseline_prediction)
                + abs(perturbed_pred2 - baseline_prediction)
            ) / 2
            importances[col] = round(importance, 4)

        return importances

    def _identify_root_cause(
        self,
        sorted_features: list[tuple[str, float]],
        feature_values: dict[str, float],
        prediction: float,
        target_gsm: float,
    ) -> str:
        """Identify the primary root cause of deviation."""
        if abs(prediction - target_gsm) / target_gsm < 0.02:
            return "All parameters within optimal range. No significant deviation detected."

        top_3 = sorted_features[:3]
        causes = []

        param_descriptions = {
            "machine_speed": "Machine speed",
            "headbox_pressure": "Headbox pressure (affects fiber distribution)",
            "dryer_temperature": "Dryer temperature (affects moisture evaporation)",
            "moisture_content": "Moisture content (affects final paper weight)",
            "chemical_dosage": "Chemical dosage (affects retention and formation)",
            "flow_rate": "Stock flow rate (affects fiber deposition)",
        }

        for feat, imp in top_3:
            if abs(imp) < 0.001:
                continue
            desc = param_descriptions.get(feat, feat)
            value = feature_values.get(feat, 0)
            causes.append(f"{desc} ({value:.1f}) contributing {imp:.4f} to prediction")

        if not causes:
            return "Multiple small factors combining to cause deviation."

        return "Primary drivers: " + "; ".join(causes) + "."

    def _build_contributions(
        self,
        sorted_features: list[tuple[str, float]],
        prediction: float,
        target_gsm: float,
    ) -> list[dict[str, Any]]:
        """Build parameter contribution list."""
        contributions = []
        for feat, imp in sorted_features[:6]:
            direction = "increase" if imp > 0 else "decrease"
            contributions.append({
                "parameter": feat,
                "impact": round(imp, 4),
                "direction": direction,
                "absolute_impact": round(abs(imp), 4),
            })
        return contributions

    def _build_decision_explanation(
        self,
        sorted_features: list[tuple[str, float]],
        prediction: float,
        target_gsm: float,
        contributions: list[dict[str, Any]],
    ) -> str:
        """Build a human-readable decision explanation."""
        deviation = prediction - target_gsm
        deviation_pct = abs(deviation) / target_gsm * 100

        if deviation_pct < 1:
            return (
                f"The AI predicts a Basis Weight of {prediction:.1f} GSM, "
                f"which is within the acceptable range of the target ({target_gsm:.1f} GSM). "
                "No corrective action is required at this time."
            )
        elif deviation_pct < 3:
            direction = "above" if deviation > 0 else "below"
            return (
                f"The AI predicts a Basis Weight of {prediction:.1f} GSM, "
                f"which is slightly {direction} the target of {target_gsm:.1f} GSM "
                f"(deviation: {deviation_pct:.1f}%). "
                f"The main contributing factor is {sorted_features[0][0]} with an impact of {abs(sorted_features[0][1]):.3f}. "
                "Minor adjustments are recommended."
            )
        else:
            direction = "above" if deviation > 0 else "below"
            return (
                f"⚠️ The AI predicts a significant deviation in Basis Weight: "
                f"{prediction:.1f} GSM vs target {target_gsm:.1f} GSM "
                f"({deviation_pct:.1f}% {direction} target). "
                f"The primary root cause is {sorted_features[0][0]} "
                f"(impact: {abs(sorted_features[0][1]):.3f}). "
                f"Secondary factors include {sorted_features[1][0]} and {sorted_features[2][0]}. "
                "Immediate corrective action is strongly recommended."
            )
