"""
============================================================
SSIP — Notebook 03: Feature Engineering
============================================================
Builds 9 custom indices + ML-ready encoded features
Inputs  : data/processed/student_success_cleaned.csv
Outputs : data/processed/student_success_processed.csv
============================================================
Indices Created:
  SSI  — Student Success Index
  EI   — Engagement Index
  PSI  — Parent Support Index
  RAI  — Resource Accessibility Index
  WBI  — Wellbeing Index
  ARI  — Academic Resilience Index
  WRI  — WAEC Readiness Index  (SS students)
  SNI  — Support Need Index
  DVI  — Dropout Vulnerability Index
============================================================
"""
import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings("ignore")

import pathlib
BASE = pathlib.Path(__file__).parent.parent
IN  = str(BASE / "data" / "processed" / "student_success_cleaned.csv")
OUT = str(BASE / "data" / "processed" / "student_success_processed.csv")

df = pd.read_csv(IN)
print(f"Loaded: {df.shape}")

# ─────────────────────────────────────────────────────────
# ORDINAL ENCODERS (for index calculations)
# ─────────────────────────────────────────────────────────

def ordinal(series, order):
    """Map ordered categories to 1..n scale."""
    mapping = {v: i+1 for i,v in enumerate(order)}
    return series.map(mapping).fillna(1).astype(float)

def norm(series, lo=None, hi=None):
    """Min-max normalise to 0-100."""
    lo = lo if lo is not None else series.min()
    hi = hi if hi is not None else series.max()
    return ((series - lo) / (hi - lo) * 100).clip(0, 100).round(2)

# Shared ordinal mappings
LOW_HIGH   = ["Very Low","Low","Moderate","High","Very High"]
POOR_EX    = ["Very Poor","Poor","Fair","Good","Excellent"]
NEVER_ALWY = ["Never","Rarely","Sometimes","Often","Always"]
UNREL_REL  = ["Very Unreliable","Unreliable","Moderate","Reliable","Very Reliable"]
NO_ACC_EX  = ["No Access","Very Poor","Poor","Fair","Good","Excellent"]

# ─────────────────────────────────────────────────────────
# INDEX 1: STUDENT SUCCESS INDEX (SSI)
# Captures academic output and consistent effort
# ─────────────────────────────────────────────────────────
att_norm  = norm(df["attendance_rate"], 0, 100)
score_norm = norm(df["average_score"],  0, 100)

ac_ord = ordinal(df["assignment_completion_rate"],
                 ["Below 50%","50-70%","71-90%","Above 90%"])
ac_norm = norm(ac_ord, 1, 4)

sh_ord  = ordinal(df["study_hours_per_day"], ["<1hr","1-2hrs","3-4hrs",">4hrs"])
sh_norm = norm(sh_ord, 1, 4)

hw_ord  = ordinal(df["homework_submission_consistency"], NEVER_ALWY[:4])
hw_norm = norm(hw_ord, 1, 4)

df["SSI"] = (
    score_norm * 0.35 +
    att_norm   * 0.25 +
    ac_norm    * 0.20 +
    sh_norm    * 0.12 +
    hw_norm    * 0.08
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 2: ENGAGEMENT INDEX (EI)
# Captures active school involvement beyond academics
# ─────────────────────────────────────────────────────────
part_ord  = ordinal(df["participation_level"], LOW_HIGH)
part_norm = norm(part_ord, 1, 5)

lib_ord   = ordinal(df["library_usage"], ["Never","Rarely","Monthly","Weekly","Daily"])
lib_norm  = norm(lib_ord, 1, 5)

pc_ord    = ordinal(df["peer_collaboration"], NEVER_ALWY)
pc_norm   = norm(pc_ord, 1, 5)

extra_ord = ordinal(df["extracurricular_involvement"],
                    ["None","1 Activity","2 Activities","3+ Activities"])
extra_norm = norm(extra_ord, 1, 4)

sat_ord   = ordinal(df["school_satisfaction"],
                    ["Very Dissatisfied","Dissatisfied","Neutral","Satisfied","Very Satisfied"])
sat_norm  = norm(sat_ord, 1, 5)

df["EI"] = (
    part_norm  * 0.30 +
    pc_norm    * 0.25 +
    lib_norm   * 0.20 +
    extra_norm * 0.15 +
    sat_norm   * 0.10
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 3: PARENT SUPPORT INDEX (PSI)
# ─────────────────────────────────────────────────────────
pi_ord   = ordinal(df["parent_involvement"], LOW_HIGH)
pi_norm  = norm(pi_ord, 1, 5)

pm_ord   = ordinal(df["parent_meeting_attendance"], NEVER_ALWY)
pm_norm  = norm(pm_ord, 1, 5)

hse_ord  = ordinal(df["home_study_environment"], POOR_EX)
hse_norm = norm(hse_ord, 1, 5)

pe_ord   = ordinal(df["parent_education_level"],
                   ["None","Primary","Secondary","OND/NCE","BSc/HND","Postgraduate"])
pe_norm  = norm(pe_ord, 1, 6)

df["PSI"] = (
    pi_norm  * 0.35 +
    pm_norm  * 0.25 +
    hse_norm * 0.25 +
    pe_norm  * 0.15
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 4: RESOURCE ACCESSIBILITY INDEX (RAI)
# ─────────────────────────────────────────────────────────
inet_ord  = ordinal(df["internet_access_quality"], NO_ACC_EX)
inet_norm = norm(inet_ord, 1, 6)

elec_ord  = ordinal(df["electricity_reliability"], UNREL_REL)
elec_norm = norm(elec_ord, 1, 5)

device_bin = (df["has_personal_device"] == "Yes").astype(float) * 100

# Distance: inverted — closer = better access
dist_inv  = norm(-df["distance_from_school_km"],
                 -df["distance_from_school_km"].max(),
                 -df["distance_from_school_km"].min())

ses_ord   = ordinal(df["socioeconomic_status"],
                    ["Low","Lower-Middle","Middle","Upper-Middle","High"])
ses_norm  = norm(ses_ord, 1, 5)

df["RAI"] = (
    inet_norm  * 0.30 +
    elec_norm  * 0.25 +
    device_bin * 0.20 +
    dist_inv   * 0.15 +
    ses_norm   * 0.10
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 5: WELLBEING INDEX (WBI)
# Higher = better wellbeing
# ─────────────────────────────────────────────────────────
# Stress inverted — less stress = higher WBI
stress_inv = ordinal(df["stress_level"], LOW_HIGH[::-1])  # Very High=1, Very Low=5
stress_inv_norm = norm(stress_inv, 1, 5)

sleep_norm = norm(df["sleep_hours_per_night"], 3, 10)

mh_ord    = ordinal(df["mental_health_indicator"], ["Poor","Concerning","Fair","Good"])
mh_norm   = norm(mh_ord, 1, 4)

pr_ord    = ordinal(df["peer_relationship_quality"], POOR_EX)
pr_norm   = norm(pr_ord, 1, 5)

# Exam anxiety inverted
ea_inv    = ordinal(df["exam_anxiety_level"], LOW_HIGH[::-1])
ea_norm   = norm(ea_inv, 1, 5)

mot_ord   = ordinal(df["motivation_level"], LOW_HIGH)
mot_norm  = norm(mot_ord, 1, 5)

df["WBI"] = (
    stress_inv_norm * 0.25 +
    mh_norm         * 0.22 +
    mot_norm        * 0.20 +
    sleep_norm      * 0.15 +
    pr_norm         * 0.10 +
    ea_norm         * 0.08
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 6: ACADEMIC RESILIENCE INDEX (ARI)
# Measures recovery, persistence, improvement
# ─────────────────────────────────────────────────────────
trend_map  = {"Improving":3, "Stable":2, "Declining":1}
trend_norm = norm(df["score_trend"].map(trend_map).fillna(2), 1, 3)

# Score delta normalised
delta_norm = norm(df["score_delta"], df["score_delta"].min(), df["score_delta"].max())

# Repeated class: already passed once (resilience signal), slight positive
repeat_bonus = (df["repeated_class"] == "Yes").astype(float) * 20

# Counselor engagement (seeking help = resilience)
counsel_norm = norm(df["counselor_visits_per_term"], 0, 5)

# High stress + pass = resilience
stress_pass_bonus = ((df["stress_level"].isin(["High","Very High"])) &
                     (df["pass_fail"] == "Pass")).astype(float) * 20

df["ARI"] = (
    trend_norm        * 0.35 +
    delta_norm        * 0.30 +
    counsel_norm      * 0.15 +
    repeat_bonus      * 0.10 +
    stress_pass_bonus * 0.10
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 7: WAEC READINESS INDEX (WRI)  — SS students only
# ─────────────────────────────────────────────────────────
ep_ord  = ordinal(df["exam_preparation_level"],
                  ["N/A","Very Poor","Poor","Fair","Good","Excellent"])
ep_norm = norm(ep_ord, 1, 6)

mock_norm = norm(df["mock_exam_score"].fillna(0), 0, 100)

# Number of WAEC subjects: 9 = max readiness
subj_norm = norm(df["waac_subject_count"].fillna(0)
                 if "waac_subject_count" in df.columns
                 else df["waec_subject_count"].fillna(0), 0, 9)

# Only meaningful for SS students
is_ss = df["is_senior_student"] == 1

df["WRI"] = 0.0
df.loc[is_ss, "WRI"] = (
    mock_norm[is_ss]  * 0.45 +
    ep_norm[is_ss]    * 0.35 +
    subj_norm[is_ss]  * 0.20
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 8: SUPPORT NEED INDEX (SNI)
# Higher = greater need for institutional support
# ─────────────────────────────────────────────────────────
# Inverted SSI
sni_academic   = (100 - df["SSI"])
# Inverted WBI
sni_wellbeing  = (100 - df["WBI"])
# Inverted PSI
sni_parent     = (100 - df["PSI"])
# Inverted RAI
sni_resource   = (100 - df["RAI"])

# Financial stress component
fs_ord         = ordinal(df["financial_stress_level"], LOW_HIGH[::-1])  # Very High=1
fs_inv         = norm(fs_ord, 1, 5)
sni_financial  = (100 - fs_inv)

df["SNI"] = (
    sni_academic  * 0.30 +
    sni_wellbeing * 0.25 +
    sni_financial * 0.22 +
    sni_resource  * 0.13 +
    sni_parent    * 0.10
).round(2)

# ─────────────────────────────────────────────────────────
# INDEX 9: DROPOUT VULNERABILITY INDEX (DVI)
# Higher = greater dropout risk
# ─────────────────────────────────────────────────────────
# Financial stress (higher stress = higher DVI)
dvi_fs    = norm(fs_ord.map(lambda x: 6-x), 1, 5)   # reverse back to Very High=5

# Attendance (low att = high DVI)
dvi_att   = norm(100 - df["attendance_rate"], 0, 100)

# Guardian type
guardian_risk = {"Both Parents":1,"Single Parent":2,"Guardian/Relative":3,"Orphan/Ward":4}
dvi_guard = norm(df["guardian_type"].map(guardian_risk).fillna(2), 1, 4)

# Tuition status
tuition_risk = {"Paid":1,"Partial":3,"Outstanding":5}
dvi_tuition  = norm(df["tuition_payment_status"].map(tuition_risk).fillna(1), 1, 5)

# Stress
dvi_stress   = norm(ordinal(df["stress_level"], LOW_HIGH), 1, 5)

# Part-time job
dvi_job      = (df["has_part_time_job"] == "Yes").astype(float) * 60

df["DVI"] = (
    dvi_fs      * 0.28 +
    dvi_att     * 0.25 +
    dvi_tuition * 0.18 +
    dvi_guard   * 0.12 +
    dvi_stress  * 0.10 +
    dvi_job     * 0.07
).round(2)

# ─────────────────────────────────────────────────────────
# ENCODE TARGETS FOR ML
# ─────────────────────────────────────────────────────────
df["pass_fail_encoded"]    = (df["pass_fail"] == "Pass").astype(int)
df["risk_level_encoded"]   = ordinal(df["risk_level"], ["Low","Medium","High","Critical"]).astype(int)
df["dropout_risk_encoded"] = ordinal(df["dropout_risk"], ["Low","Medium","High"]).astype(int)

# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
indices = ["SSI","EI","PSI","RAI","WBI","ARI","WRI","SNI","DVI"]
print(f"\n{'='*55}")
print(f"  Custom Indices Summary")
print(f"{'='*55}")
print(f"  {'Index':<6}  {'Mean':>7}  {'Std':>7}  {'Min':>7}  {'Max':>7}")
print(f"  {'-'*49}")
for idx in indices:
    s = df[idx]
    print(f"  {idx:<6}  {s.mean():>7.1f}  {s.std():>7.1f}  {s.min():>7.1f}  {s.max():>7.1f}")

print(f"\n  Final shape : {df.shape}")
print(f"  New columns : {len(df.columns)} (raw 63 + 9 indices + 5 derived + 3 encoded targets)")

# Cross-index correlations
corr = df[indices].corr().round(2)
print(f"\n  Index correlations (key pairs):")
print(f"  SSI ↔ EI   : {corr.loc['SSI','EI']}")
print(f"  DVI ↔ SSI  : {corr.loc['DVI','SSI']}")
print(f"  WBI ↔ SSI  : {corr.loc['WBI','SSI']}")
print(f"  SNI ↔ DVI  : {corr.loc['SNI','DVI']}")
print(f"  PSI ↔ SSI  : {corr.loc['PSI','SSI']}")
print(f"  RAI ↔ SSI  : {corr.loc['RAI','SSI']}")

df.to_csv(OUT, index=False)
print(f"\n✅ Processed dataset saved → {OUT}")
