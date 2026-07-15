"""GradeWise AI - Model Training Script.

Usage:
    python -m app.ml.models.train

This script:
1. Loads synthetic (or real) production data
2. Runs feature engineering
3. Trains and compares multiple ML models
4. Saves the best model for deployment
"""

import sys
from pathlib import Path

import pandas as pd

from app.ml.data.synthetic_generator import generate_full_synthetic_dataset
from app.ml.models.registry import ModelRegistry
from app.ml.pipeline.feature_engineering import FeatureEngineer


def main():
    """Run the model training pipeline."""
    print("=" * 60)
    print("  GradeWise AI — Model Training Pipeline")
    print("=" * 60)

    # 1. Generate or load data
    data_dir = Path("data/synthetic")
    steady_state_path = data_dir / "steady_state_production.csv"

    if not steady_state_path.exists():
        print("\n[1/4] Generating synthetic dataset...")
        generate_full_synthetic_dataset(str(data_dir))

    print("\n[1/4] Loading training data...")
    df = pd.read_csv(steady_state_path)
    print(f"  → Loaded {len(df):,} samples with {len(df.columns)} columns")

    # 2. Feature engineering
    print("\n[2/4] Running feature engineering...")
    engineer = FeatureEngineer(
        use_rolling_features=True,
        use_lag_features=True,
        use_interaction_features=True,
    )
    X = engineer.fit_transform(df)
    print(f"  → Engineered {len(engineer.get_feature_names())} features")

    # 3. Train models
    print("\n[3/4] Training and comparing models...")
    registry = ModelRegistry(
        models_dir="ml/models/saved",
        experiment_name="basis_weight_prediction_v1",
    )

    results = registry.train_and_compare(df)
    print(f"  → Best model: {results['best_model_type']}")
    print(f"  → Version: {results['version']}")
    print(f"  → RMSE: {results['metrics']['rmse_mean']:.4f}")
    print(f"  → MAE: {results['metrics']['mae_mean']:.4f}")
    print(f"  → R²: {results['metrics']['r2_mean']:.4f}")
    print(f"  → Model saved to: {results['model_path']}")

    # 4. Summary
    print("\n[4/4] Training complete!")
    print(f"\n  Model Comparison:")
    for name, metrics in results["all_results"].items():
        print(f"    {name:25s}  RMSE={metrics['rmse_mean']:.4f}  "
              f"MAE={metrics['mae_mean']:.4f}  R²={metrics['r2_mean']:.4f}")

    print("\n" + "=" * 60)
    print("  Pipeline ready for prediction serving.")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
