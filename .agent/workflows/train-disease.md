# /train-disease Workflow

1. Verify raw image dataset exists in `ml/data/raw/` (e.g., PlantVillage).
2. Execute `python ml/train_disease.py`.
3. Check that stratified 70/15/15 split was applied with random seed 42.
4. Verify artifacts are generated under `app/ml_artifacts/disease/`:
   - `model.keras`
   - `class_names.json`
   - `metrics.json` (accuracy, macro-F1, per-class precision and recall)
   - `confusion_matrix.png`
   - `training_curves.png`
5. If `ml/data/field_test/` exists, execute `python ml/evaluate.py` to record field test accuracy.
6. Display metrics summary and confusion matrix for Checkpoint 4b.
