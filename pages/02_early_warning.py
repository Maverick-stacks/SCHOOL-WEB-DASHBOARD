"""SSIP — Early Warning Center ⭐ WOW Feature #1"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, PAGE_HEADER, RISK_COLORS, risk_badge

st.set_page_config(page_title="SSIP | Early Warning Center", layout="wide")

PAGE_HEADER("🚨 Early Warning Center",
            "Students who need immediate attention — identified before failure occurs")

df = load_data()

# ── Alert Summary ─────────────────────────────────────────
critical = df[df["risk_level"]=="Critical"]
high     = df[df["risk_level"]=="High"]
hi_drop  = df[df["dropout_risk"]=="High"]
declining= df[df["score_trend"]=="Declining"]

st.markdown("""
<div style="background:#1c1917;border:1px solid #dc2626;border-radius:14px;
     padding:20px 28px;margin-bottom:20px;">
  <h3 style="color:#fca5a5;margin:0 0 8px 0;">⚠️ Active Alerts</h3>
  <p style="color:#d1d5db;margin:0;">The following students require immediate institutional attention.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔴 Critical Risk", len(critical), "Immediate action required", delta_color="inverse")
c2.metric("🟠 High Risk",     len(high),     "Intervention recommended",  delta_color="inverse")
c3.metric("📉 Declining",     len(declining),"Score trend worsening",     delta_color="inverse")
c4.metric("⚠️ Dropout Risk",  len(hi_drop),  "High probability",          delta_color="inverse")

st.markdown("---")

# ── Filters ───────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    show_risk = st.multiselect("Risk Level", ["Critical","High","Medium"],
                                default=["Critical","High"])
with col_f2:
    show_drop = st.multiselect("Dropout Risk", ["High","Medium","Low"],
                                default=["High","Medium"])
with col_f3:
    class_filter = st.multiselect("Class", sorted(df["class_level"].unique()),
                                   default=sorted(df["class_level"].unique()))

alerts = df[
    (df["risk_level"].isin(show_risk)) &
    (df["dropout_risk"].isin(show_drop)) &
    (df["class_level"].isin(class_filter))
].copy()

st.markdown(f"### 📋 At-Risk Student List ({len(alerts)} students)")

if len(alerts) == 0:
    st.info("No students match the selected filters.")
else:
    # Add risk score for sorting
    risk_sort = {"Critical":4,"High":3,"Medium":2,"Low":1}
    drop_sort = {"High":3,"Medium":2,"Low":1}
    alerts["_risk_n"]  = alerts["risk_level"].map(risk_sort)
    alerts["_drop_n"]  = alerts["dropout_risk"].map(drop_sort)
    alerts = alerts.sort_values(["_risk_n","_drop_n"], ascending=False)

    # Display table
    display_cols = [
        "student_id","class_level","gender","average_score","attendance_rate",
        "financial_stress_level","stress_level","score_trend",
        "risk_level","dropout_risk","pass_fail"
    ]
    disp = alerts[[c for c in display_cols if c in alerts.columns]].copy()
    disp.columns = [c.replace("_"," ").title() for c in disp.columns]

    # Color-code risk level
    def highlight_risk(row):
        colors = {"Critical":"background-color:#1c0606;color:#fca5a5",
                  "High":    "background-color:#1c0a06;color:#fdba74",
                  "Medium":  "background-color:#1c1506;color:#fde68a",
                  "Low":     "background-color:#061c0c;color:#86efac"}
        r = row.get("Risk Level", "Low")
        style = colors.get(r, "")
        return [style if c == "Risk Level" else "" for c in row.index]

    st.dataframe(
        disp.style.apply(highlight_risk, axis=1),
        use_container_width=True, height=400
    )

    st.markdown("---")
    # ── Risk Factor Heatmap ───────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🌡️ Risk Factors Distribution")
        top_alerts = alerts.head(200)
        factors = ["attendance_rate","average_score","SSI","WBI","PSI","RAI","DVI"]
        factors = [f for f in factors if f in top_alerts.columns]
        factor_means = top_alerts[factors].mean().reset_index()
        factor_means.columns = ["Factor","Value"]
        school_means = df[factors].mean().reset_index()
        school_means.columns = ["Factor","School Avg"]
        comparison = factor_means.merge(school_means, on="Factor")

        fig = go.Figure()
        fig.add_trace(go.Bar(name="At-Risk Students", x=comparison["Factor"],
                             y=comparison["Value"], marker_color="#dc2626"))
        fig.add_trace(go.Bar(name="School Average", x=comparison["Factor"],
                             y=comparison["School Avg"], marker_color="#3b82f6"))
        fig.update_layout(barmode="group", paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                          font_color="#e2e8f0", height=320,
                          margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### 📚 Primary Challenges (At-Risk Students)")
        if "primary_challenge" in alerts.columns:
            keywords = ["internet","electricity","mathematics","financial","stress",
                        "health","transport","workload","family","confidence"]
            keyword_counts = {k: alerts["primary_challenge"].str.lower().str.contains(k).sum()
                              for k in keywords}
            kw_df = pd.DataFrame(list(keyword_counts.items()), columns=["Challenge","Count"])
            kw_df = kw_df.sort_values("Count", ascending=True)
            fig2 = px.bar(kw_df, x="Count", y="Challenge", orientation="h",
                          color="Count", color_continuous_scale=["#1e3a5f","#dc2626"])
            fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                               font_color="#e2e8f0", height=320,
                               margin=dict(t=10,b=10,l=10,r=10), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Intervention Recommendations ──────────────────────
    st.markdown("---")
    st.markdown("### 💡 Recommended Interventions")

    interventions = {
        "low_attendance":  (alerts["attendance_rate"] < 65).sum(),
        "low_score":       (alerts["average_score"] < 50).sum(),
        "financial_stress":(alerts["financial_stress_level"].isin(["Very High","High"])).sum(),
        "high_stress":     (alerts["stress_level"].isin(["Very High","High"])).sum(),
        "parent_support":  (alerts["parent_involvement"].isin(["Very Low","Low"])).sum(),
        "declining_scores":(alerts["score_trend"]=="Declining").sum(),
    }

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        n = interventions["low_attendance"]
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:16px;border-left:4px solid #3b82f6;">
          <h4 style="color:#93c5fd;margin:0 0 8px 0;">📅 Attendance Recovery</h4>
          <p style="color:#e2e8f0;font-size:1.4rem;font-weight:700;margin:0;">{n} students</p>
          <p style="color:#94a3b8;font-size:0.8rem;margin:6px 0 0 0;">
            Attendance &lt; 65% — requires attendance plan + parent notification
          </p>
        </div>""", unsafe_allow_html=True)
    with ic2:
        n = interventions["financial_stress"]
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:16px;border-left:4px solid #d97706;">
          <h4 style="color:#fcd34d;margin:0 0 8px 0;">💰 Financial Support</h4>
          <p style="color:#e2e8f0;font-size:1.4rem;font-weight:700;margin:0;">{n} students</p>
          <p style="color:#94a3b8;font-size:0.8rem;margin:6px 0 0 0;">
            Very High/High financial stress — scholarship or payment plan referral
          </p>
        </div>""", unsafe_allow_html=True)
    with ic3:
        n = interventions["high_stress"]
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:16px;border-left:4px solid #8b5cf6;">
          <h4 style="color:#c4b5fd;margin:0 0 8px 0;">💚 Counseling Support</h4>
          <p style="color:#e2e8f0;font-size:1.4rem;font-weight:700;margin:0;">{n} students</p>
          <p style="color:#94a3b8;font-size:0.8rem;margin:6px 0 0 0;">
            High/Very High stress — counselor session + wellbeing check-in
          </p>
        </div>""", unsafe_allow_html=True)
