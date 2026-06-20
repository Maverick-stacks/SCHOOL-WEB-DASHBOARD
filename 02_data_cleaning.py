"""
============================================================
SSIP — Notebook 02: Data Cleaning
============================================================
Inputs  : data/raw/student_success_dataset.csv
Outputs : data/processed/student_success_cleaned.csv
          reports/outputs/cleaning_report.txt
============================================================
"""
import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings("ignore")

import pathlib
BASE = pathlib.Path(__file__).parent.parent
RAW  = str(BASE / "data" / "raw" / "student_success_dataset.csv")
OUT  = str(BASE / "data" / "processed" / "student_success_cleaned.csv")
RPT  = str(BASE / "reports" / "outputs" / "cleaning_report.txt")
os.makedirs(str(BASE / "data" / "processed"), exist_ok=True)
os.makedirs(str(BASE / "reports" / "outputs"), exist_ok=True)

report = []
def log(msg=""):
    print(msg); report.append(msg)

log("="*60)
log("  SSIP — Data Cleaning Report")
log("="*60)

# ── 1. LOAD ───────────────────────────────────────────────
df = pd.read_csv(RAW)
log(f"\n[1] RAW DATASET")
log(f"    Shape     : {df.shape}")
log(f"    Students  : {len(df)}")
log(f"    Columns   : {len(df.columns)}")

# ── 2. DTYPES ────────────────────────────────────────────
log(f"\n[2] DATA TYPES")
numeric_cols = [
    "distance_from_school_km","commute_time_minutes","number_of_siblings",
    "sleep_hours_per_night","attendance_rate","math_score","english_score",
    "science_score","social_studies_score","average_score",
    "prev_math_score","prev_english_score","prev_science_score",
    "prev_social_studies_score","prev_average_score","counselor_visits_per_term",
    "mock_exam_score","waec_subject_count","meals_per_day"
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

categorical_cols = [c for c in df.columns if c not in numeric_cols
                    and c not in ["student_id","primary_challenge","support_needed"]]
for c in categorical_cols:
    if c in df.columns:
        df[c] = df[c].astype("category")

log(f"    Numeric cols converted   : {len(numeric_cols)}")
log(f"    Categorical cols flagged : {len(categorical_cols)}")

# ── 3. MISSING VALUES ────────────────────────────────────
log(f"\n[3] MISSING VALUES")
missing = df.isnull().sum()
missing = missing[missing > 0]
log(f"    Columns with nulls:")
for col, cnt in missing.items():
    log(f"      {col:<35} {cnt:>5} ({cnt/len(df)*100:.1f}%)")

# WAEC columns are N/A for JSS students — expected
# Numeric WAEC → 0 for JSS (will be handled by WRI index in FE)
waec_numeric = ["mock_exam_score","waec_subject_count"]
for c in waec_numeric:
    df[c] = df[c].fillna(0)

# exam_preparation_level: fill JSS with "N/A" string
df["exam_preparation_level"] = df["exam_preparation_level"].astype(str).replace("nan","N/A")
df["exam_preparation_level"] = df["exam_preparation_level"].astype("category")

log(f"\n    After WAEC fill → remaining nulls: {df.isnull().sum().sum()}")

# ── 4. DUPLICATE CHECK ───────────────────────────────────
log(f"\n[4] DUPLICATES")
dups = df.duplicated().sum()
log(f"    Duplicate rows   : {dups}")
log(f"    Duplicate IDs    : {df['student_id'].duplicated().sum()}")

# ── 5. RANGE / CONSISTENCY CHECKS ───────────────────────
log(f"\n[5] RANGE & CONSISTENCY CHECKS")
issues = []

score_cols = ["math_score","english_score","science_score","social_studies_score",
              "average_score","prev_math_score","prev_english_score",
              "prev_science_score","prev_social_studies_score","prev_average_score"]
for c in score_cols:
    oob = ((df[c]<0) | (df[c]>100)).sum()
    if oob: issues.append(f"  {c}: {oob} out-of-range values")

att_oob = ((df["attendance_rate"]<0) | (df["attendance_rate"]>100)).sum()
if att_oob: issues.append(f"  attendance_rate: {att_oob} out-of-range")

sleep_oob = ((df["sleep_hours_per_night"]<2) | (df["sleep_hours_per_night"]>14)).sum()
if sleep_oob: issues.append(f"  sleep_hours: {sleep_oob} suspicious values")

# Age-class consistency check
age_class_map = {"10-12":["JSS1","JSS2"], "13-15":["JSS2","JSS3","SS1"], "16-18":["SS1","SS2","SS3"]}
df["age_class_flag"] = False
for age_grp, valid_classes in age_class_map.items():
    mask = (df["age_group"]==age_grp) & (~df["class_level"].isin(valid_classes))
    df.loc[mask, "age_class_flag"] = True
flags = df["age_class_flag"].sum()
if flags: issues.append(f"  age/class mismatch flags: {flags} (minor, due to repeaters)")
df.drop(columns=["age_class_flag"], inplace=True)

if issues:
    for i in issues: log(f"  ⚠  {i}")
else:
    log("    ✅ All range checks passed")

# Clamp scores to [0, 100] just in case
for c in score_cols:
    df[c] = df[c].clip(0, 100)

# ── 6. STANDARDISE CATEGORY VALUES ──────────────────────
log(f"\n[6] CATEGORY STANDARDISATION")
cat_fixes = 0
for c in df.select_dtypes("category").columns:
    # strip whitespace
    df[c] = df[c].cat.rename_categories(
        lambda x: str(x).strip() if isinstance(x, str) else x
    )
    cat_fixes += 1
log(f"    Stripped whitespace in {cat_fixes} categorical columns")

# ── 7. DERIVED CLEANING COLUMNS ─────────────────────────
log(f"\n[7] DERIVED FLAG COLUMNS (for EDA & ML)")

# Score improvement flag
df["score_improved"] = (df["average_score"] > df["prev_average_score"]).astype(int)
df["score_delta"]    = (df["average_score"] - df["prev_average_score"]).round(1)

# Attendance category (bucketed for EDA)
df["attendance_category"] = pd.cut(
    df["attendance_rate"],
    bins=[0,50,65,75,85,100],
    labels=["Critical (<50%)","Low (50-65%)","Fair (65-75%)","Good (75-85%)","Excellent (85%+)"],
    right=True
)

# Average score category
df["score_category"] = pd.cut(
    df["average_score"],
    bins=[0,39,49,59,69,79,100],
    labels=["Failing (<40)","Poor (40-49)","Below Avg (50-59)","Average (60-69)","Good (70-79)","Excellent (80+)"],
    right=True
)

# Is SS student flag (for WAEC-specific analyses)
df["is_senior_student"] = df["class_level"].isin(["SS1","SS2","SS3"]).astype(int)

log(f"    score_improved       : binary flag")
log(f"    score_delta          : numeric improvement over previous term")
log(f"    attendance_category  : 5-bucket attendance band")
log(f"    score_category       : 6-bucket performance band")
log(f"    is_senior_student    : JSS=0, SS=1")

# ── 8. FINAL SUMMARY ────────────────────────────────────
log(f"\n[8] CLEANED DATASET SUMMARY")
log(f"    Final shape     : {df.shape}")
log(f"    Remaining nulls : {df.isnull().sum().sum()}")
log(f"\n    Pass/Fail distribution:")
vc = df["pass_fail"].value_counts(normalize=True).round(3)
for k,v in vc.items(): log(f"      {k}: {v*100:.1f}%")
log(f"\n    Risk Level distribution:")
vc2 = df["risk_level"].value_counts()
for k,v in vc2.items(): log(f"      {k}: {v}")
log(f"\n    Score delta (avg improvement vs prev term): {df['score_delta'].mean():.2f}")

# ── SAVE ─────────────────────────────────────────────────
df.to_csv(OUT, index=False)
with open(RPT, "w", encoding="utf-8") as f: f.write("\n".join(report))
log(f"\n✅ Cleaned data saved  → {OUT}")
log(f"✅ Cleaning report     → {RPT}")
log("="*60)
