"""
============================================================
SSIP — Notebook 06: Machine Learning Pipeline
============================================================
Models:
  1. Pass/Fail Classification   → LogisticRegression, RandomForest
  2. Final Score Regression     → RandomForestRegressor
  3. Academic Risk Classification → RandomForest (4-class)
  4. Dropout Risk Classification → GradientBoosting (XGBoost-equivalent)

Outputs: /models/*.pkl
         /reports/outputs/ml_report.txt
============================================================
"""
import pandas as pd, numpy as np, os, warnings, joblib
warnings.filterwarnings("ignore")

from sklearn.model_selection    import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing      import LabelEncoder, StandardScaler, OrdinalEncoder
from sklearn.linear_model       import LogisticRegression
from sklearn.ensemble           import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.pipeline           import Pipeline
from sklearn.compose            import ColumnTransformer
from sklearn.impute             import SimpleImputer
from sklearn.metrics            import (accuracy_score, classification_report,
                                        confusion_matrix, roc_auc_score,
                                        mean_absolute_error, r2_score,
                                        mean_squared_error)

import pathlib
BASE = pathlib.Path(__file__).parent.parent
os.makedirs(str(BASE / "models"), exist_ok=True)
os.makedirs(str(BASE / "reports" / "outputs"), exist_ok=True)

report = []
def log(msg=""):
    print(msg); report.append(str(msg))

log("="*62)
log("  SSIP — Machine Learning Pipeline")
log("="*62)

# ── Load ─────────────────────────────────────────────────
df = pd.read_csv(str(BASE / "data" / "processed" / "student_success_processed.csv"))
log(f"\nDataset: {df.shape[0]} students | {df.shape[1]} features")

# ── Feature sets ─────────────────────────────────────────
NUMERIC_FEATURES = [
    "attendance_rate","average_score","prev_average_score",
    "math_score","english_score","science_score","social_studies_score",
    "prev_math_score","prev_english_score","prev_science_score","prev_social_studies_score",
    "score_delta","sleep_hours_per_night","distance_from_school_km",
    "commute_time_minutes","counselor_visits_per_term","number_of_siblings",
    "meals_per_day",
    # All 9 custom indices
    "SSI","EI","PSI","RAI","WBI","ARI","WRI","SNI","DVI",
]

CATEGORICAL_FEATURES = [
    "gender","class_level","socioeconomic_status","guardian_type",
    "parent_education_level","parent_involvement","home_study_environment",
    "internet_access_quality","has_personal_device","electricity_reliability",
    "financial_stress_level","tuition_payment_status","has_part_time_job",
    "stress_level","mental_health_indicator","exam_anxiety_level","motivation_level",
    "participation_level","extracurricular_involvement","peer_collaboration",
    "study_hours_per_day","assignment_completion_rate","homework_submission_consistency",
    "teacher_accessibility_rating","receives_extra_tutoring","score_trend",
    "boarding_status","receives_scholarship",
]

# Validate columns exist
NUMERIC_FEATURES   = [c for c in NUMERIC_FEATURES   if c in df.columns]
CATEGORICAL_FEATURES = [c for c in CATEGORICAL_FEATURES if c in df.columns]

log(f"Numeric features    : {len(NUMERIC_FEATURES)}")
log(f"Categorical features: {len(CATEGORICAL_FEATURES)}")
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# ── Preprocessor ─────────────────────────────────────────
numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])
categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
])
preprocessor = ColumnTransformer([
    ("num", numeric_transformer,  NUMERIC_FEATURES),
    ("cat", categorical_transformer, CATEGORICAL_FEATURES),
])

def evaluate_classifier(model, X_train, X_test, y_train, y_test, name, cv=True):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc  = accuracy_score(y_test, y_pred)
    log(f"\n  ── {name} ──")
    log(f"  Accuracy      : {acc:.4f}  ({acc*100:.1f}%)")
    if cv:
        skf    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scr = cross_val_score(model, X_train, y_train, cv=skf, scoring="accuracy")
        log(f"  CV Accuracy   : {cv_scr.mean():.4f} ± {cv_scr.std():.4f}")
    try:
        y_prob = model.predict_proba(X_test)
        if y_prob.shape[1] == 2:
            auc = roc_auc_score(y_test, y_prob[:,1])
            log(f"  ROC-AUC       : {auc:.4f}")
        else:
            auc = roc_auc_score(y_test, y_prob, multi_class="ovr", average="weighted")
            log(f"  ROC-AUC (OvR) : {auc:.4f}")
    except Exception: pass
    log(f"\n  Classification Report:\n{classification_report(y_test, y_pred, zero_division=0)}")
    return model

# ════════════════════════════════════════════════════════
# MODEL 1: PASS / FAIL PREDICTION
# ════════════════════════════════════════════════════════
log("\n" + "="*62)
log("  MODEL 1 — Pass/Fail Prediction (Binary Classification)")
log("="*62)

X = df[ALL_FEATURES].copy()
y = (df["pass_fail"] == "Pass").astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y)
log(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")
log(f"Class balance (train) — Pass: {y_train.mean()*100:.1f}% | Fail: {(1-y_train.mean())*100:.1f}%")

# Logistic Regression
lr_pipeline = Pipeline([
    ("prep", preprocessor),
    ("clf",  LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"))
])
lr_pipeline = evaluate_classifier(lr_pipeline, X_train, X_test, y_train, y_test, "Logistic Regression")

# Random Forest (best model saved)
rf_pf_pipeline = Pipeline([
    ("prep", preprocessor),
    ("clf",  RandomForestClassifier(n_estimators=200, max_depth=12,
                                     min_samples_leaf=5, class_weight="balanced",
                                     random_state=42, n_jobs=-1))
])
rf_pf_pipeline = evaluate_classifier(rf_pf_pipeline, X_train, X_test, y_train, y_test, "Random Forest")

# Feature importance
rf_model = rf_pf_pipeline.named_steps["clf"]
feature_names = (NUMERIC_FEATURES +
    list(rf_pf_pipeline.named_steps["prep"]
         .named_transformers_["cat"]
         .named_steps["encoder"]
         .get_feature_names_out() if hasattr(
         rf_pf_pipeline.named_steps["prep"]
         .named_transformers_["cat"]
         .named_steps["encoder"], "get_feature_names_out") else CATEGORICAL_FEATURES))
importances = rf_model.feature_importances_
fi_df = pd.DataFrame({"feature": feature_names[:len(importances)],
                       "importance": importances}).sort_values("importance", ascending=False)
log("\n  Top 10 Feature Importances (Pass/Fail):")
for _, row in fi_df.head(10).iterrows():
    log(f"    {row['feature']:<35} {row['importance']:.4f}")

joblib.dump(rf_pf_pipeline, str(BASE / "models" / "pass_fail_model.pkl"))
joblib.dump(lr_pipeline,    str(BASE / "models" / "logistic_pass_fail_model.pkl"))
log("\n  ✅ pass_fail_model.pkl saved")

# ════════════════════════════════════════════════════════
# MODEL 2: ACADEMIC RISK CLASSIFICATION (4-class)
# ════════════════════════════════════════════════════════
log("\n" + "="*62)
log("  MODEL 2 — Academic Risk Classification (Low/Medium/High/Critical)")
log("="*62)

y_risk = df["risk_level"].astype(str)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_risk, test_size=0.20, random_state=42, stratify=y_risk)
log(f"\nClass distribution:\n{y_risk.value_counts().to_string()}")

rf_risk_pipeline = Pipeline([
    ("prep", preprocessor),
    ("clf",  RandomForestClassifier(n_estimators=200, max_depth=15,
                                     min_samples_leaf=3, class_weight="balanced",
                                     random_state=42, n_jobs=-1))
])
rf_risk_pipeline = evaluate_classifier(rf_risk_pipeline, X_train, X_test,
                                        y_train, y_test, "Random Forest — Risk", cv=True)
joblib.dump(rf_risk_pipeline, str(BASE / "models" / "risk_model.pkl"))
log("  ✅ risk_model.pkl saved")

# ════════════════════════════════════════════════════════
# MODEL 3: DROPOUT RISK PREDICTION
# ════════════════════════════════════════════════════════
log("\n" + "="*62)
log("  MODEL 3 — Dropout Risk Prediction (Low/Medium/High)")
log("="*62)

y_drop = df["dropout_risk"].astype(str)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_drop, test_size=0.20, random_state=42, stratify=y_drop)
log(f"\nClass distribution:\n{y_drop.value_counts().to_string()}")

gb_drop_pipeline = Pipeline([
    ("prep", preprocessor),
    ("clf",  GradientBoostingClassifier(n_estimators=200, max_depth=5,
                                         learning_rate=0.05, subsample=0.8,
                                         random_state=42))
])
gb_drop_pipeline = evaluate_classifier(gb_drop_pipeline, X_train, X_test,
                                        y_train, y_test, "GradientBoosting — Dropout", cv=False)
joblib.dump(gb_drop_pipeline, str(BASE / "models" / "dropout_model.pkl"))
log("  ✅ dropout_model.pkl saved")

# ════════════════════════════════════════════════════════
# MODEL 4: FINAL SCORE REGRESSION (GPA Prediction)
# ════════════════════════════════════════════════════════
log("\n" + "="*62)
log("  MODEL 4 — Final Score Regression (Average Score Prediction)")
log("="*62)

# Exclude current average_score from features to avoid leakage
REGRESSION_FEATURES_NUM = [c for c in NUMERIC_FEATURES
                             if c not in ["average_score","SSI","SNI"]]
REGRESSION_FEATURES_CAT = CATEGORICAL_FEATURES

reg_preprocessor = ColumnTransformer([
    ("num", numeric_transformer,    REGRESSION_FEATURES_NUM),
    ("cat", categorical_transformer, REGRESSION_FEATURES_CAT),
])

X_reg = df[REGRESSION_FEATURES_NUM + REGRESSION_FEATURES_CAT].copy()
y_reg = df["average_score"]
X_train, X_test, y_train, y_test = train_test_split(
    X_reg, y_reg, test_size=0.20, random_state=42)

rf_reg_pipeline = Pipeline([
    ("prep", reg_preprocessor),
    ("reg",  RandomForestRegressor(n_estimators=200, max_depth=12,
                                    min_samples_leaf=5, random_state=42, n_jobs=-1))
])
rf_reg_pipeline.fit(X_train, y_train)
y_pred_reg = rf_reg_pipeline.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred_reg)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_reg))
r2   = r2_score(y_test, y_pred_reg)
log(f"\n  RandomForest Regressor")
log(f"  MAE   : {mae:.2f} points")
log(f"  RMSE  : {rmse:.2f} points")
log(f"  R²    : {r2:.4f}")

joblib.dump(rf_reg_pipeline, str(BASE / "models" / "final_score_model.pkl"))
log("  ✅ final_score_model.pkl saved")

# ── Save scaler + encoder separately for dashboard use ───
joblib.dump(preprocessor, str(BASE / "models" / "preprocessor.pkl"))
joblib.dump({"numeric": NUMERIC_FEATURES, "categorical": CATEGORICAL_FEATURES,
             "all": ALL_FEATURES}, str(BASE / "models" / "feature_columns.pkl"))
log("\n  ✅ preprocessor.pkl saved")
log("  ✅ feature_columns.pkl saved")

# ── Final summary ─────────────────────────────────────────
log("\n" + "="*62)
log("  MODEL ARTIFACTS SAVED")
log("="*62)
for f in os.listdir(str(BASE / "models")):
    size = os.path.getsize(str(BASE / "models" / f)) / 1024
    log(f"  {f:<40} {size:>8.1f} KB")

with open(str(BASE / "reports" / "outputs" / "ml_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
log("\n✅ ML pipeline complete → reports/outputs/ml_report.txt")
