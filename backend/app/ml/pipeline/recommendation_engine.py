"""GradeWise AI - Recommendation Engine.

Generates optimal machine setting recommendations based on predictions,
explainability results, and historical transition data.
"""

from typing import Any, Optional

import numpy as np

# Parameter adjustment rules based on domain knowledge
# Each rule: (parameter, direction_if_gsm_too_low, direction_if_gsm_too_high, step_size, description)

PARAMETER_ADJUSTMENT_RULES = {
    "machine_speed": {
        "name": "Machine Speed",
        "unit": "m/min",
        "adjustment_low": "decrease",
        "adjustment_high": "increase",
        "step_percent": 3.0,
        "min_value": 400,
        "max_value": 1200,
        "explanation_low": "Decreasing machine speed allows more fiber deposition per unit area, increasing GSM.",
        "explanation_high": "Increasing machine speed reduces fiber deposition, lowering GSM toward target.",
    },
    "headbox_pressure": {
        "name": "Headbox Pressure",
        "unit": "bar",
        "adjustment_low": "increase",
        "adjustment_high": "decrease",
        "step_percent": 2.0,
        "min_value": 1.5,
        "max_value": 4.5,
        "explanation_low": "Increasing headbox pressure improves fiber distribution, raising GSM.",
        "explanation_high": "Decreasing headbox pressure reduces stock jet velocity, lowering GSM.",
    },
    "dryer_temperature": {
        "name": "Dryer Temperature",
        "unit": "°C",
        "adjustment_low": "decrease",
        "adjustment_high": "increase",
        "step_percent": 2.5,
        "min_value": 80,
        "max_value": 160,
        "explanation_low": "Lower dryer temperature retains more moisture, increasing final GSM.",
        "explanation_high": "Higher dryer temperature removes more moisture, reducing final GSM.",
    },
    "moisture_content": {
        "name": "Moisture Content",
        "unit": "%",
        "adjustment_low": "increase",
        "adjustment_high": "decrease",
        "step_percent": 5.0,
        "min_value": 3.0,
        "max_value": 9.0,
        "explanation_low": "Higher moisture content increases paper weight, raising GSM.",
        "explanation_high": "Lower moisture content reduces water weight, lowering GSM.",
    },
    "chemical_dosage": {
        "name": "Chemical Dosage",
        "unit": "kg/ton",
        "adjustment_low": "increase",
        "adjustment_high": "decrease",
        "step_percent": 4.0,
        "min_value": 0.5,
        "max_value": 3.5,
        "explanation_low": "Increasing chemical dosage improves retention, raising GSM.",
        "explanation_high": "Decreasing chemical dosage reduces retention, lowering GSM.",
    },
    "flow_rate": {
        "name": "Flow Rate",
        "unit": "L/min",
        "adjustment_low": "increase",
        "adjustment_high": "decrease",
        "step_percent": 3.0,
        "min_value": 1500,
        "max_value": 4000,
        "explanation_low": "Increasing flow rate deposits more fibers, raising GSM.",
        "explanation_high": "Decreasing flow rate deposits fewer fibers, lowering GSM.",
    },
}


class RecommendationEngine:
    """Generates optimal machine setting recommendations with reasoning."""

    def __init__(self):
        self.param_rules = PARAMETER_ADJUSTMENT_RULES

    def generate_recommendations(
        self,
        current_values: dict[str, float],
        predicted_gsm: float,
        target_gsm: float,
        feature_importance: dict[str, float],
        confidence: float,
        model: Any = None,
    ) -> dict[str, Any]:
        """Generate a set of recommended parameter adjustments.

        Args:
            current_values: Current machine parameter readings
            predicted_gsm: Model's predicted basis weight
            target_gsm: Target basis weight for the current grade
            feature_importance: Feature importance from explainability
            confidence: Model prediction confidence
            model: Optional model for what-if evaluation

        Returns:
            Dict with recommended settings, expected improvement, and reasoning
        """
        deviation = predicted_gsm - target_gsm
        deviation_pct = abs(deviation) / target_gsm * 100

        if deviation_pct < 1.0:
            return {
                "recommended_settings": {},
                "expected_basis_weight": predicted_gsm,
                "expected_improvement": {"gsm_change": 0, "deviation_reduction": 0},
                "confidence": confidence,
                "reasoning": "Current settings are producing acceptable results. No adjustments needed.",
                "status": "optimal",
            }

        direction = "low" if deviation < 0 else "high"

        # Prioritize parameters by feature importance
        sorted_params = sorted(
            feature_importance.items(), key=lambda x: abs(x[1]), reverse=True
        )

        recommended_changes = {}
        reasoning_parts = []

        cumulative_adjustment = 0.0

        for param, importance in sorted_params:
            if param not in self.param_rules:
                continue
            if abs(importance) < 0.001:
                continue

            rules = self.param_rules[param]
            current_val = current_values.get(param, 0)
            if current_val == 0:
                continue

            # Determine adjustment direction
            adjustment_dir = rules[f"adjustment_{direction}"]
            step = current_val * (rules["step_percent"] / 100)

            if adjustment_dir == "increase":
                new_val = min(current_val + step, rules["max_value"])
                change = new_val - current_val
            else:
                new_val = max(current_val - step, rules["min_value"])
                change = new_val - current_val

            # Only recommend if meaningful change
            if abs(change) / current_val < 0.005:
                continue

            recommended_changes[param] = {
                "current": round(current_val, 2),
                "recommended": round(new_val, 2),
                "change": round(change, 2),
                "direction": adjustment_dir,
                "unit": rules["unit"],
                "display_name": rules["name"],
                "importance": round(abs(importance), 4),
            }

            explanation = rules[f"explanation_{direction}"]
            reasoning_parts.append(f"• {rules['name']}: {explanation}")

            # Estimate GSM impact of this change
            gsm_impact = -change * np.sign(deviation) * abs(importance) * 10
            cumulative_adjustment += gsm_impact

        # Calculate expected improvement
        expected_new_gsm = predicted_gsm + cumulative_adjustment
        new_deviation = abs(expected_new_gsm - target_gsm) / target_gsm * 100

        # Build comprehensive reasoning
        if not reasoning_parts:
            reasoning = "Unable to generate specific recommendations. Manual operator intervention recommended."
        else:
            deviation_desc = "decrease" if deviation < 0 else "increase"
            reasoning = (
                f"The current Basis Weight ({predicted_gsm:.1f} GSM) is {direction} "
                f"relative to the target ({target_gsm:.1f} GSM). "
                f"To correct this {deviation_pct:.1f}% {deviation_desc}, "
                f"the following adjustments are recommended:\n\n"
                + "\n".join(reasoning_parts)
            )

        # Sort recommendations by importance
        sorted_recommendations = dict(
            sorted(
                recommended_changes.items(),
                key=lambda x: x[1]["importance"],
                reverse=True,
            )
        )

        return {
            "recommended_settings": sorted_recommendations,
            "expected_basis_weight": round(expected_new_gsm, 2),
            "expected_improvement": {
                "gsm_change": round(cumulative_adjustment, 2),
                "deviation_reduction_pct": round(deviation_pct - max(new_deviation, 0), 2),
                "new_deviation_pct": round(new_deviation, 2),
                "estimated_waste_reduction_kg": round(abs(cumulative_adjustment) * 2.5, 2),
            },
            "confidence": confidence,
            "reasoning": reasoning,
            "status": "recommended",
        }

    def simulate_what_if(
        self,
        current_values: dict[str, float],
        modified_values: dict[str, float],
        model: Any,
        feature_engineer: Any,
        target_gsm: float,
    ) -> dict[str, Any]:
        """Simulate the effect of parameter changes on predicted GSM.

        This functions as a digital twin — operators can adjust sliders
        and instantly see the predicted outcome.
        """
        # Start with current values, apply modifications
        sim_values = {**current_values, **modified_values}

        df = pd.DataFrame([sim_values])
        for feat in feature_engineer.features:  # type: ignore[union-attr]
            if feat not in df.columns:
                df[feat] = 0.0
        import pandas as pd

        try:
            X = feature_engineer.transform(df)
            predicted = float(model.predict(X)[0])
        except Exception:
            # Fallback heuristic
            predicted = target_gsm
            for param, val in modified_values.items():
                delta = val - current_values.get(param, val)
                predicted += delta * 0.5

        deviation = predicted - target_gsm
        deviation_pct = abs(deviation) / target_gsm * 100

        if deviation_pct <= 2:
            risk = "green"
        elif deviation_pct <= 5:
            risk = "yellow"
        else:
            risk = "red"

        waste_reduction = max(0, (abs(current_values.get("basis_weight", predicted) - target_gsm) - abs(deviation)) * 2.5)

        parameter_changes = {
            param: {
                "from": round(current_values.get(param, 0), 2),
                "to": round(val, 2),
                "delta": round(val - current_values.get(param, 0), 2),
            }
            for param, val in modified_values.items()
        }

        if deviation_pct < 1:
            impact = "✅ Minimal impact — production well within target."
        elif deviation_pct < 3:
            impact = "🟡 Moderate impact — acceptable with monitoring."
        else:
            impact = "🔴 Significant impact — review parameter changes before applying."

        return {
            "predicted_basis_weight": round(predicted, 2),
            "risk_level": risk,
            "confidence": 0.85,
            "deviation_from_target": round(deviation_pct, 2),
            "estimated_waste_reduction_kg": round(waste_reduction, 2),
            "production_impact": impact,
            "parameter_changes": parameter_changes,
        }
