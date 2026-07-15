"""GradeWise AI - What-If Simulator Routes."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.schemas import WhatIfRequest, WhatIfResponse

router = APIRouter()


@router.post("/simulate", response_model=WhatIfResponse)
async def run_what_if_simulation(request: WhatIfRequest):
    """Run a digital twin simulation with modified parameters.

    Operators can adjust machine parameters via sliders and instantly
    see the predicted impact on basis weight, risk level, and waste.
    """
    import numpy as np

    # Base prediction using process physics model
    target_gsm = 100.0  # In production: from production run's target grade
    base_speed = 800.0
    base_pressure = 2.5
    base_dryer = 120.0
    base_moisture = 5.5
    base_chem = 1.8
    base_flow = 2500.0

    # Compute prediction with modified parameters
    predicted = target_gsm
    predicted += -0.015 * (request.machine_speed - base_speed)
    predicted += 0.4 * (request.headbox_pressure - base_pressure) * 10
    predicted += -0.15 * (request.dryer_temperature - base_dryer)
    predicted += 0.8 * (request.moisture_content - base_moisture)
    predicted += 0.5 * (request.chemical_dosage - base_chem) * 5
    predicted += 0.004 * (request.flow_rate - base_flow)
    predicted += np.random.normal(0, target_gsm * 0.005)  # Small noise

    deviation_pct = abs(predicted - target_gsm) / target_gsm * 100

    if deviation_pct <= 2:
        risk_level = "green"
        confidence = 0.92
    elif deviation_pct <= 5:
        risk_level = "yellow"
        confidence = 0.78
    else:
        risk_level = "red"
        confidence = 0.60

    # Estimate waste reduction
    waste_reduction = max(0, (5 - deviation_pct) * 3.5)

    if deviation_pct < 1:
        impact = "✅ Minimal impact — production well within target range."
    elif deviation_pct < 3:
        impact = "🟡 Moderate impact — acceptable with continuous monitoring."
    else:
        impact = "🔴 Significant impact — review parameter changes before applying."

    # Build parameter changes from base values
    parameter_changes = {
        "machine_speed": {
            "from": base_speed,
            "to": request.machine_speed,
            "delta": round(request.machine_speed - base_speed, 2),
        },
        "headbox_pressure": {
            "from": base_pressure,
            "to": request.headbox_pressure,
            "delta": round(request.headbox_pressure - base_pressure, 2),
        },
        "dryer_temperature": {
            "from": base_dryer,
            "to": request.dryer_temperature,
            "delta": round(request.dryer_temperature - base_dryer, 2),
        },
    }

    return WhatIfResponse(
        predicted_basis_weight=round(float(predicted), 2),
        risk_level=risk_level,
        confidence=round(confidence, 2),
        deviation_from_target=round(deviation_pct, 2),
        estimated_waste_reduction=round(waste_reduction, 2),
        production_impact=impact,
        parameter_changes=parameter_changes,
    )
