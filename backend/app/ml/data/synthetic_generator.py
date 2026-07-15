"""GradeWise AI - Synthetic Data Generator for Paper Manufacturing.

Generates realistic synthetic data that closely mimics industrial paper manufacturing
process data. The data structure is designed so that swapping with real plant data
requires minimal code changes — simply replace the data source.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ── Paper Grade Definitions ────────────────────────────

PAPER_GRADES = [
    {"name": "70 GSM Copy Paper", "gsm_target": 70.0, "gsm_tolerance_min": 68.0, "gsm_tolerance_max": 72.0},
    {"name": "80 GSM Bond Paper", "gsm_target": 80.0, "gsm_tolerance_min": 78.0, "gsm_tolerance_max": 82.0},
    {"name": "90 GSM Ledger Paper", "gsm_target": 90.0, "gsm_tolerance_min": 88.0, "gsm_tolerance_max": 92.0},
    {"name": "100 GSM Cover Paper", "gsm_target": 100.0, "gsm_tolerance_min": 97.0, "gsm_tolerance_max": 103.0},
    {"name": "120 GSM Card Stock", "gsm_target": 120.0, "gsm_tolerance_min": 117.0, "gsm_tolerance_max": 123.0},
    {"name": "150 GSM Heavy Card", "gsm_target": 150.0, "gsm_tolerance_min": 147.0, "gsm_tolerance_max": 153.0},
    {"name": "200 GSM Board", "gsm_target": 200.0, "gsm_tolerance_min": 196.0, "gsm_tolerance_max": 204.0},
    {"name": "250 GSM Box Board", "gsm_target": 250.0, "gsm_tolerance_min": 245.0, "gsm_tolerance_max": 255.0},
    {"name": "300 GSM Heavy Board", "gsm_target": 300.0, "gsm_tolerance_min": 294.0, "gsm_tolerance_max": 306.0},
    {"name": "350 GSM Industrial Board", "gsm_target": 350.0, "gsm_tolerance_min": 343.0, "gsm_tolerance_max": 357.0},
]

# ── Machine Operating Parameters ──────────────────────

MACHINE_PARAM_RANGES = {
    "machine_speed": (400.0, 1200.0),       # m/min
    "headbox_pressure": (1.5, 4.5),          # bar
    "dryer_temperature": (80.0, 160.0),      # °C
    "moisture_content": (3.0, 9.0),          # %
    "chemical_dosage": (0.5, 3.5),           # kg/ton
    "flow_rate": (1500.0, 4000.0),           # L/min
    "vacuum_pressure": (-0.8, -0.2),         # bar
    "wire_tension": (4.0, 8.0),              # kN/m
    "press_load": (80.0, 160.0),             # kN/m
    "stock_consistency": (0.5, 1.5),         # %
    "ambient_temperature": (18.0, 38.0),     # °C
    "ambient_humidity": (30.0, 80.0),        # %
}


def generate_sensor_readings(
    grade: dict,
    num_samples: int = 500,
    noise_level: float = 0.05,
    drift_rate: float = 0.0002,
    with_anomalies: bool = True,
    seed: Optional[int] = None,
) -> pd.DataFrame:
    """Generate synthetic sensor readings for a paper grade production run.

    The data simulates realistic process dynamics including:
    - Steady-state production with natural process noise
    - Periodic drift in parameters
    - Occasional anomalies and deviations
    - Grade-dependent baseline parameter values

    Args:
        grade: Paper grade definition dict
        num_samples: Number of sensor readings to generate
        noise_level: Process noise magnitude
        drift_rate: Parameter drift rate per sample
        with_anomalies: Include production anomalies
        seed: Random seed for reproducibility

    Returns:
        DataFrame with sensor readings
    """
    if seed is not None:
        np.random.seed(seed)

    gsm_target = grade["gsm_target"]
    timestamps = [
        datetime(2026, 1, 1, 0, 0, 0) + timedelta(minutes=i)
        for i in range(num_samples)
    ]

    # Baseline parameters that correlate with GSM target
    base_speed = 800.0 - (gsm_target - 70.0) * 1.2  # Higher GSM → slower speed
    base_pressure = 2.5 + (gsm_target - 70.0) * 0.005  # Slightly higher for heavier paper
    base_dryer_temp = 120.0 + (gsm_target - 70.0) * 0.08  # More drying for heavier paper
    base_moisture = 5.5 - (gsm_target - 70.0) * 0.003
    base_chem_dosage = 1.8 + (gsm_target - 70.0) * 0.004
    base_flow_rate = 2500.0 + (gsm_target - 70.0) * 6.0

    # Generate time series with drift and noise
    t = np.arange(num_samples)

    machine_speed = base_speed + drift_rate * base_speed * t + noise_level * base_speed * np.random.randn(num_samples)
    headbox_pressure = base_pressure + 0.0001 * t + noise_level * base_pressure * np.random.randn(num_samples)
    dryer_temperature = base_dryer_temp + 0.0005 * t + noise_level * base_dryer_temp * np.random.randn(num_samples)
    moisture_content = base_moisture + 0.0001 * t + noise_level * base_moisture * np.random.randn(num_samples)
    chemical_dosage = base_chem_dosage + 0.0001 * t + noise_level * base_chem_dosage * np.random.randn(num_samples)
    flow_rate = base_flow_rate + 0.01 * t + noise_level * base_flow_rate * np.random.randn(num_samples)

    # Keep within realistic ranges
    machine_speed = np.clip(machine_speed, 300, 1300)
    headbox_pressure = np.clip(headbox_pressure, 1.0, 5.5)
    dryer_temperature = np.clip(dryer_temperature, 60, 180)
    moisture_content = np.clip(moisture_content, 1.0, 12.0)
    chemical_dosage = np.clip(chemical_dosage, 0.2, 5.0)
    flow_rate = np.clip(flow_rate, 1000, 5000)

    # Compute basis weight with realistic physics-inspired relationship
    # GSM ∝ flow_rate / machine_speed ∝ stock_consistency
    # Also affected by moisture, pressure, dryer temp
    basis_weight = (
        gsm_target
        + 0.02 * (machine_speed - base_speed)
        + 0.15 * (headbox_pressure - base_pressure) * 10
        - 0.1 * (dryer_temperature - base_dryer_temp) * 0.5
        - 0.3 * (moisture_content - base_moisture) * 2
        + 0.1 * (chemical_dosage - base_chem_dosage) * 5
        + 0.0008 * (flow_rate - base_flow_rate)
    )

    # Add process noise to GSM
    basis_weight += noise_level * gsm_target * np.random.randn(num_samples)

    # Inject anomalies
    if with_anomalies:
        anomaly_indices = np.random.choice(num_samples, size=max(3, num_samples // 50), replace=False)
        for idx in anomaly_indices:
            anomaly_type = np.random.choice(["spike", "drift", "oscillation"])
            if anomaly_type == "spike":
                basis_weight[idx:idx+5] += np.random.choice([-1, 1]) * gsm_target * 0.08 * np.random.rand()
            elif anomaly_type == "drift":
                drift_length = min(20, num_samples - idx)
                basis_weight[idx:idx+drift_length] += np.linspace(0, gsm_target * 0.06 * np.random.choice([-1, 1]), drift_length)
            elif anomaly_type == "oscillation":
                osc_length = min(15, num_samples - idx)
                basis_weight[idx:idx+osc_length] += gsm_target * 0.04 * np.sin(np.linspace(0, 3 * np.pi, osc_length))

    # Additional sensor values
    vacuum_pressure = -0.5 + 0.05 * np.random.randn(num_samples)
    wire_tension = 6.0 + 0.5 * np.random.randn(num_samples)
    press_load = 120.0 + 10.0 * np.random.randn(num_samples)
    stock_consistency = 1.0 + 0.15 * np.random.randn(num_samples)
    ambient_temperature = 28.0 + 5.0 * np.random.randn(num_samples)
    ambient_humidity = 55.0 + 15.0 * np.random.randn(num_samples)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "basis_weight": basis_weight,
        "gsm_target": gsm_target,
        "grade_name": grade["name"],
        "machine_speed": machine_speed,
        "headbox_pressure": headbox_pressure,
        "dryer_temperature": dryer_temperature,
        "moisture_content": moisture_content,
        "chemical_dosage": chemical_dosage,
        "flow_rate": flow_rate,
        "vacuum_pressure": vacuum_pressure,
        "wire_tension": wire_tension,
        "press_load": press_load,
        "stock_consistency": stock_consistency,
        "ambient_temperature": ambient_temperature,
        "ambient_humidity": ambient_humidity,
    })

    return df


def generate_grade_transition_data(
    from_grade: dict,
    to_grade: dict,
    transition_duration_minutes: int = 30,
    stabilization_minutes: int = 60,
    seed: Optional[int] = None,
) -> pd.DataFrame:
    """Generate synthetic data for a grade transition between two grades.

    Simulates the dynamic process of switching from one paper grade to another,
    including the transition period and subsequent stabilization.
    """
    if seed is not None:
        np.random.seed(seed)

    total_minutes = transition_duration_minutes + stabilization_minutes
    timestamps = [
        datetime(2026, 1, 1, 0, 0, 0) + timedelta(minutes=i)
        for i in range(total_minutes)
    ]

    from_gsm = from_grade["gsm_target"]
    to_gsm = to_grade["gsm_target"]
    gsm_diff = to_gsm - from_gsm

    t = np.arange(total_minutes)
    transition_progress = np.clip(t / transition_duration_minutes, 0, 1)

    # Smooth S-curve transition
    smooth_transition = 1 / (1 + np.exp(-12 * (transition_progress - 0.5)))

    # Target GSM during transition
    target_gsm = from_gsm + gsm_diff * smooth_transition

    # Parameter adjustments during transition
    base_speed_from = 800.0 - (from_gsm - 70.0) * 1.2
    base_speed_to = 800.0 - (to_gsm - 70.0) * 1.2
    machine_speed = base_speed_from + (base_speed_to - base_speed_from) * smooth_transition

    base_pressure_from = 2.5 + (from_gsm - 70.0) * 0.005
    base_pressure_to = 2.5 + (to_gsm - 70.0) * 0.005
    headbox_pressure = base_pressure_from + (base_pressure_to - base_pressure_from) * smooth_transition

    base_dryer_from = 120.0 + (from_gsm - 70.0) * 0.08
    base_dryer_to = 120.0 + (to_gsm - 70.0) * 0.08
    dryer_temperature = base_dryer_from + (base_dryer_to - base_dryer_from) * smooth_transition

    # Add process noise
    noise = 0.03
    machine_speed += noise * machine_speed * np.random.randn(total_minutes)
    headbox_pressure += noise * headbox_pressure * np.random.randn(total_minutes)
    dryer_temperature += noise * dryer_temperature * np.random.randn(total_minutes)

    moisture_content = 5.5 + noise * 2.0 * np.random.randn(total_minutes)
    moisture_content = np.clip(moisture_content, 1.0, 12.0)

    chemical_dosage = 1.8 + noise * 0.5 * np.random.randn(total_minutes)
    flow_rate = 2500.0 + noise * 200.0 * np.random.randn(total_minutes)

    # Actual basis weight with some deviation
    actual_basis_weight = target_gsm + 2.0 * np.random.randn(total_minutes)

    # Stabilization: deviation decreases over time in stabilization phase
    stabilization_mask = t >= transition_duration_minutes
    decay = np.exp(-0.05 * (t[stabilization_mask] - transition_duration_minutes))
    actual_basis_weight[stabilization_mask] = (
        to_gsm + (actual_basis_weight[stabilization_mask] - to_gsm) * decay
    )

    df = pd.DataFrame({
        "timestamp": timestamps,
        "basis_weight": actual_basis_weight,
        "target_gsm": target_gsm,
        "from_grade": from_grade["name"],
        "to_grade": to_grade["name"],
        "from_gsm": from_gsm,
        "to_gsm": to_gsm,
        "transition_progress": transition_progress,
        "machine_speed": machine_speed,
        "headbox_pressure": headbox_pressure,
        "dryer_temperature": dryer_temperature,
        "moisture_content": moisture_content,
        "chemical_dosage": chemical_dosage,
        "flow_rate": flow_rate,
        "is_stabilized": stabilization_mask,
    })

    return df


def generate_operator_logs(
    num_entries: int = 200,
    seed: Optional[int] = None,
) -> pd.DataFrame:
    """Generate synthetic operator activity logs."""
    if seed is not None:
        np.random.seed(seed)

    action_types = [
        "parameter_change", "grade_change_initiated",
        "recommendation_accepted", "recommendation_rejected",
        "recommendation_modified", "alert_acknowledged",
        "manual_override", "comment",
    ]

    operators = ["Operator_01", "Operator_02", "Operator_03", "Engineer_01", "Supervisor_01"]

    timestamps = [
        datetime(2026, 1, 1, 0, 0, 0) + timedelta(minutes=i * 30)
        for i in range(num_entries)
    ]

    actions = np.random.choice(action_types, size=num_entries)
    ops = np.random.choice(operators, size=num_entries)

    records = []
    for ts, action, op in zip(timestamps, actions, ops):
        records.append({
            "timestamp": ts,
            "action_type": action,
            "operator_id": op,
            "details": f"{op} performed {action}",
        })

    return pd.DataFrame(records)


def generate_full_synthetic_dataset(
    output_dir: str = "data/synthetic",
    seed: int = 42,
) -> dict[str, str]:
    """Generate the complete synthetic dataset for GradeWise AI.

    Returns:
        Dict mapping dataset name to output file path.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    np.random.seed(seed)

    files = {}

    # 1. Generate steady-state data for each grade
    all_steady_state = []
    for grade in PAPER_GRADES:
        df = generate_sensor_readings(grade, num_samples=500, seed=seed)
        all_steady_state.append(df)

    steady_state_df = pd.concat(all_steady_state, ignore_index=True)
    path = str(output_path / "steady_state_production.csv")
    steady_state_df.to_csv(path, index=False)
    files["steady_state"] = path

    # 2. Generate grade transition data
    all_transitions = []
    for i in range(len(PAPER_GRADES)):
        for j in range(len(PAPER_GRADES)):
            if i != j and abs(i - j) <= 3:  # Limit to nearby grade transitions
                from_grade = PAPER_GRADES[i]
                to_grade = PAPER_GRADES[j]
                df = generate_grade_transition_data(
                    from_grade, to_grade,
                    transition_duration_minutes=30,
                    stabilization_minutes=45,
                    seed=seed + i * 10 + j,
                )
                all_transitions.append(df)

    transitions_df = pd.concat(all_transitions, ignore_index=True)
    path = str(output_path / "grade_transitions.csv")
    transitions_df.to_csv(path, index=False)
    files["transitions"] = path

    # 3. Operator logs
    operator_df = generate_operator_logs(num_entries=300, seed=seed)
    path = str(output_path / "operator_logs.csv")
    operator_df.to_csv(path, index=False)
    files["operator_logs"] = path

    # 4. Save paper grades reference
    grades_df = pd.DataFrame(PAPER_GRADES)
    path = str(output_path / "paper_grades.csv")
    grades_df.to_csv(path, index=False)
    files["paper_grades"] = path

    # 5. Summary stats
    summary = {
        "num_grades": len(PAPER_GRADES),
        "num_steady_state_samples": len(steady_state_df),
        "num_transition_samples": len(transitions_df),
        "num_operator_logs": len(operator_df),
        "gsm_range": f"{PAPER_GRADES[0]['gsm_target']}-{PAPER_GRADES[-1]['gsm_target']}",
        "parameters": list(MACHINE_PARAM_RANGES.keys()),
    }
    path = str(output_path / "dataset_summary.json")
    import json
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    files["summary"] = path

    return files


if __name__ == "__main__":
    files = generate_full_synthetic_dataset()
    for name, path in files.items():
        print(f"Generated {name}: {path}")
