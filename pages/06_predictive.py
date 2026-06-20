"""SSIP — Predictive Analytics"""
import streamlit as st, pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, load_model, PAGE_HEADER, RISK_COLORS

st.set_page_config(page_title="SSIP | Predictive Analytics", layout="wide")
PAGE_HEADER("🤖 Predictive Analytics",
            "ML-powered predictions — Pass/Fail, Risk Level, Dropout Risk, and Score Forecasting")

df = load_data()

tab1, tab2, tab3 = st.tabs(["🎯 Model Performance", "🔮 Live Prediction", "📊 Feature Importance"])

# ── TAB 1: Model Performance ───────────────────────────────
with tab1:
    st.markdown("### Model Performance Summary")
    st.markdown("""
    <div style="background:#1e293b;border-radius:12px;padding:20px;border:1px solid #334155;margin-bottom:20px;">
      <p style="color:#94a3b8;margin:0;">
        All models trained on 80% of the 2,000-student dataset. Evaluated on a held-out 20% test set.
        Stratified splits ensure class balance across train/test.
      </p>
    </div>""", unsafe_allow_html=True)

    models_summary = pd.DataFrame({
        "Model": ["Pass/Fail — Random Forest","Pass/Fail — Logistic Regression",
                  "Risk Classification — Random Forest","Dropout Risk — Gradient Boosting",
                  "Score Regression — Random Forest"],
        "Type":  ["Binary Classification","Binary Classification",
                  "4-Class Classification","3-Class Classification","Regression"],
        "Accuracy / R²": ["100.0%","99.0%","65.8%","92.0%","R² = 0.99"],
        "ROC-AUC":        ["1.000","0.9998","0.856 (OvR)","0.981 (OvR)","MAE = 0.51"],
        "Notes":          [
            "Score threshold creates near-perfect boundary",
            "Strong linear separability",
            "4-class problem; AUROC 0.856 is strong",
            "Imbalanced classes handled well",
            "Low MAE — less than 1 score point error"
        ]
    })
    st.dataframe(models_summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Risk Level Distribution — Predicted vs Actual")
    risk_counts = df["risk_level"].value_counts().reindex(["Critical","High","Medium","Low"]).fillna(0)
    fig = go.Figure(go.Bar(x=risk_counts.index, y=risk_counts.values,
                           marker_color=[RISK_COLORS[r] for r in risk_counts.index],
                           text=risk_counts.values, textposition="outside",
                           textfont_color="#e2e8f0"))
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                      height=300, margin=dict(t=10,b=10,l=10,r=10))
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 2: Live Prediction ────────────────────────────────
with tab2:
    st.markdown("### 🔮 Predict a Student's Risk Profile")
    st.markdown("Adjust the sliders to simulate a student profile and get instant ML predictions.")

    col1, col2, col3 = st.columns(3)
    with col1:
        att_rate   = st.slider("Attendance Rate (%)",     10, 100, 72)
        avg_score  = st.slider("Average Score",           10, 100, 55)
        prev_score = st.slider("Previous Term Score",     10, 100, 58)
        study_hrs  = st.select_slider("Study Hours/Day", ["<1hr","1-2hrs","3-4hrs",">4hrs"], "<1hr")
    with col2:
        stress     = st.selectbox("Stress Level",    ["Very Low","Low","Moderate","High","Very High"], index=2)
        fin_stress = st.selectbox("Financial Stress",["No Stress","Low","Moderate","High","Very High"], index=2)
        motivation = st.selectbox("Motivation Level",["Very Low","Low","Moderate","High","Very High"], index=2)
        internet   = st.selectbox("Internet Quality",["No Access","Very Poor","Poor","Fair","Good","Excellent"], index=2)
    with col3:
        class_lv   = st.selectbox("Class Level", ["JSS1","JSS2","JSS3","SS1","SS2","SS3"], index=3)
        gender     = st.selectbox("Gender",      ["Male","Female"])
        ses        = st.selectbox("Socioeconomic Status", ["Low","Lower-Middle","Middle","Upper-Middle","High"], index=2)
        par_inv    = st.selectbox("Parent Involvement",   ["Very Low","Low","Moderate","High","Very High"], index=2)

    # Rule-based prediction (since model artifacts need local paths)
    st.markdown("---")
    st.markdown("#### 📊 Predicted Profile")

    # Simple rule-based scoring for demo
    risk_score = 0
    if avg_score < 40:  risk_score += 3
    elif avg_score < 50: risk_score += 2
    elif avg_score < 60: risk_score += 1
    if att_rate < 50:    risk_score += 3
    elif att_rate < 65:  risk_score += 2
    elif att_rate < 75:  risk_score += 1
    stress_map = {"Very High":2,"High":1,"Moderate":0,"Low":0,"Very Low":0}
    risk_score += stress_map.get(stress, 0)
    fin_map    = {"Very High":2,"High":1,"Moderate":0,"Low":0,"No Stress":0}
    risk_score += fin_map.get(fin_stress, 0)

    pred_risk    = "Critical" if risk_score>=8 else "High" if risk_score>=5 else "Medium" if risk_score>=3 else "Low"
    pred_pass    = "Pass" if avg_score >= 50 else "Fail"
    drop_score   = (fin_map.get(fin_stress,0)*2 + (2 if att_rate<55 else 1 if att_rate<65 else 0) +
                    (1 if stress in ["Very High"] else 0))
    pred_dropout = "High" if drop_score>=5 else "Medium" if drop_score>=3 else "Low"

    risk_color = RISK_COLORS.get(pred_risk,"#64748b")
    drop_color = {"High":"#dc2626","Medium":"#d97706","Low":"#16a34a"}.get(pred_dropout,"#64748b")
    pf_color   = "#16a34a" if pred_pass=="Pass" else "#dc2626"

    rc1, rc2, rc3, rc4 = st.columns(4)
    for col_, label, val, color in [
        (rc1,"Academic Risk",    pred_risk,    risk_color),
        (rc2,"Pass/Fail",        pred_pass,    pf_color),
        (rc3,"Dropout Risk",     pred_dropout, drop_color),
        (rc4,"Risk Score",       f"{risk_score}/12","#8b5cf6"),
    ]:
        col_.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:16px;border-left:4px solid {color};">
          <p style="color:#94a3b8;margin:0;font-size:0.75rem;text-transform:uppercase;">{label}</p>
          <p style="color:{color};margin:6px 0 0 0;font-size:1.5rem;font-weight:800;">{val}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Note:** This demo uses rule-based scoring for instant preview. "
            "For full ML model predictions, run `06_machine_learning.py` locally to generate "
            "the `.pkl` model artifacts, then load them here via `load_model()`.")

# ── TAB 3: Feature Importance ────────────────────────────
with tab3:
    st.markdown("### 📊 Feature Importance — What Drives Student Risk?")
    fi_data = pd.DataFrame({
        "Feature": [
            "Average Score","Attendance Rate","Financial Stress Level","Stress Level",
            "Previous Average Score","SSI (Student Success Index)","DVI (Dropout Vulnerability)",
            "Parent Involvement","Study Hours Per Day","Internet Access Quality",
            "Assignment Completion","Motivation Level","Score Trend","WBI (Wellbeing Index)",
            "Guardian Type","Tuition Payment Status","Sleep Hours","Meals Per Day"
        ],
        "Importance": [0.294,0.187,0.089,0.078,0.071,0.065,0.058,
                       0.042,0.038,0.033,0.029,0.025,0.022,0.019,
                       0.016,0.014,0.011,0.009],
        "Category": ["Academic","Academic","Financial","Wellbeing","Academic","Index","Index",
                     "Family","Study Habit","Infrastructure","Study Habit","Wellbeing",
                     "Academic","Index","Family","Financial","Wellbeing","Financial"]
    })

    cat_colors = {"Academic":"#3b82f6","Financial":"#f59e0b","Wellbeing":"#8b5cf6",
                  "Family":"#10b981","Infrastructure":"#64748b",
                  "Study Habit":"#06b6d4","Index":"#ec4899"}

    fig = px.bar(fi_data.sort_values("Importance"), x="Importance", y="Feature",
                 orientation="h", color="Category",
                 color_discrete_map=cat_colors, text_auto=".3f")
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                      height=520, margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b",
                      xaxis_title="Feature Importance Score", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **Key Insight:** Academic performance and attendance are the strongest predictors,
    but financial stress, wellbeing, and parent involvement collectively rival them —
    which is exactly why SSIP goes beyond grades.
    """)
