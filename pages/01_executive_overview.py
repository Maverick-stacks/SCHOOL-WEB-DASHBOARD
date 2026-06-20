"""SSIP — Executive Overview"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, metric_card, PAGE_HEADER, RISK_COLORS

st.set_page_config(page_title="SSIP | Executive Overview", layout="wide")

PAGE_HEADER("📊 Executive Overview",
            "Current state of the school — performance, risk, and key trends at a glance")

df = load_data()

# ── Filters ───────────────────────────────────────────────
with st.expander("🔧 Filters", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        classes = st.multiselect("Class Level", sorted(df["class_level"].unique()),
                                  default=sorted(df["class_level"].unique()))
    with col2:
        gender = st.multiselect("Gender", df["gender"].unique(), default=list(df["gender"].unique()))
    with col3:
        term   = st.selectbox("View", ["All Students","Senior Only (SS1-SS3)","Junior Only (JSS1-JSS3)"])

filtered = df[df["class_level"].isin(classes) & df["gender"].isin(gender)]
if term == "Senior Only (SS1-SS3)":   filtered = filtered[filtered["is_senior_student"]==1]
elif term == "Junior Only (JSS1-JSS3)": filtered = filtered[filtered["is_senior_student"]==0]

# ── KPI Row ───────────────────────────────────────────────
st.markdown("### 🏫 School Health Dashboard")
c1,c2,c3,c4,c5,c6 = st.columns(6)

total    = len(filtered)
pass_rt  = (filtered["pass_fail"]=="Pass").mean()*100
avg_sc   = filtered["average_score"].mean()
avg_att  = filtered["attendance_rate"].mean()
at_risk  = (filtered["risk_level"].isin(["High","Critical"])).sum()
hi_drop  = (filtered["dropout_risk"]=="High").sum()

c1.markdown(metric_card("Total Students",  f"{total:,}",  color="#3b82f6"),   unsafe_allow_html=True)
c2.markdown(metric_card("Pass Rate",       f"{pass_rt:.1f}%", color="#16a34a"), unsafe_allow_html=True)
c3.markdown(metric_card("Avg Score",       f"{avg_sc:.1f}",   color="#8b5cf6"), unsafe_allow_html=True)
c4.markdown(metric_card("Avg Attendance",  f"{avg_att:.1f}%", color="#0ea5e9"), unsafe_allow_html=True)
c5.markdown(metric_card("High Risk",       f"{at_risk}",  "Need intervention",  color="#ea580c"), unsafe_allow_html=True)
c6.markdown(metric_card("Dropout Risk",    f"{hi_drop}",  "Immediate attention",color="#dc2626"), unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: Charts ─────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Risk Level Distribution")
    risk_counts = filtered["risk_level"].value_counts().reindex(["Critical","High","Medium","Low"]).fillna(0)
    fig = go.Figure(go.Bar(
        x=risk_counts.index, y=risk_counts.values,
        marker_color=[RISK_COLORS[r] for r in risk_counts.index],
        text=risk_counts.values, textposition="outside",
        textfont=dict(color="#e2e8f0")
    ))
    fig.update_layout(
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font_color="#e2e8f0", xaxis_title="", yaxis_title="Students",
        margin=dict(t=20,b=20,l=20,r=20), height=280
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Pass Rate by Class Level")
    pass_by_class = (filtered.groupby("class_level")["pass_fail"]
                     .apply(lambda x: (x=="Pass").mean()*100)
                     .reset_index())
    pass_by_class.columns = ["Class","Pass Rate (%)"]
    class_order = ["JSS1","JSS2","JSS3","SS1","SS2","SS3"]
    pass_by_class["Class"] = pd.Categorical(pass_by_class["Class"], class_order, ordered=True)
    pass_by_class = pass_by_class.sort_values("Class")
    fig2 = px.bar(pass_by_class, x="Class", y="Pass Rate (%)",
                  color="Pass Rate (%)",
                  color_continuous_scale=["#dc2626","#d97706","#16a34a"],
                  range_color=[50,100], text_auto=".1f")
    fig2.update_traces(textposition="outside", textfont=dict(color="#e2e8f0"))
    fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                       font_color="#e2e8f0", height=280,
                       margin=dict(t=20,b=20,l=20,r=20), coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 3 ─────────────────────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("#### Score Distribution")
    fig3 = px.histogram(filtered, x="average_score", nbins=30,
                        color_discrete_sequence=["#3b82f6"])
    fig3.add_vline(x=50, line_dash="dash", line_color="#dc2626",
                   annotation_text="Pass threshold", annotation_font_color="#dc2626")
    fig3.add_vline(x=avg_sc, line_dash="dash", line_color="#16a34a",
                   annotation_text=f"Mean: {avg_sc:.1f}", annotation_font_color="#16a34a")
    fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                       font_color="#e2e8f0", height=280,
                       margin=dict(t=20,b=20,l=20,r=20),
                       xaxis_title="Average Score", yaxis_title="Students")
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown("#### Attendance vs Score (Risk Overlay)")
    sample = filtered.sample(min(500, len(filtered)), random_state=42)
    fig4 = px.scatter(sample, x="attendance_rate", y="average_score",
                      color="risk_level",
                      color_discrete_map=RISK_COLORS,
                      opacity=0.7, size_max=6,
                      category_orders={"risk_level":["Critical","High","Medium","Low"]},
                      hover_data=["student_id","class_level"])
    fig4.add_hline(y=50, line_dash="dash", line_color="#dc2626", opacity=0.5)
    fig4.add_vline(x=75, line_dash="dash", line_color="#d97706", opacity=0.5)
    fig4.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                       font_color="#e2e8f0", height=280,
                       margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 4: Index Overview ─────────────────────────────────
st.markdown("---")
st.markdown("### 📈 Custom Intelligence Indices — School Averages")

indices = ["SSI","EI","PSI","RAI","WBI","ARI","WRI","SNI","DVI"]
idx_labels = {
    "SSI":"Student Success","EI":"Engagement","PSI":"Parent Support",
    "RAI":"Resource Access","WBI":"Wellbeing","ARI":"Academic Resilience",
    "WRI":"WAEC Readiness","SNI":"Support Need","DVI":"Dropout Vulnerability"
}
cols = st.columns(len(indices))
for i, idx in enumerate(indices):
    val = filtered[idx].mean()
    color = "#dc2626" if idx in ["SNI","DVI"] and val>50 else \
            "#16a34a" if val>60 else "#d97706"
    cols[i].metric(idx_labels[idx], f"{val:.1f}", f"↑ Avg" if val>50 else f"↓ Avg")

# ── Row 5: SES breakdown ──────────────────────────────────
st.markdown("---")
col_e, col_f = st.columns(2)
with col_e:
    st.markdown("#### Average Score by Socioeconomic Status")
    ses_order = ["Low","Lower-Middle","Middle","Upper-Middle","High"]
    ses_scores = (filtered.groupby("socioeconomic_status")["average_score"]
                  .mean().reindex(ses_order).reset_index())
    fig5 = px.bar(ses_scores, x="socioeconomic_status", y="average_score",
                  color="average_score",
                  color_continuous_scale=["#dc2626","#d97706","#16a34a"],
                  range_color=[40,75], text_auto=".1f")
    fig5.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                       font_color="#e2e8f0", height=260,
                       margin=dict(t=10,b=10,l=10,r=10), coloraxis_showscale=False,
                       xaxis_title="SES", yaxis_title="Avg Score")
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.markdown("#### Dropout Risk by Financial Stress")
    cross = (pd.crosstab(filtered["financial_stress_level"],
                         filtered["dropout_risk"], normalize="index")*100).round(1)
    fig6 = px.bar(cross.reset_index().melt(id_vars="financial_stress_level"),
                  x="financial_stress_level", y="value", color="dropout_risk",
                  color_discrete_map={"High":"#dc2626","Medium":"#d97706","Low":"#16a34a"},
                  barmode="stack", text_auto=".0f")
    fig6.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                       font_color="#e2e8f0", height=260,
                       margin=dict(t=10,b=10,l=10,r=10),
                       xaxis_title="Financial Stress", yaxis_title="% Students",
                       legend_title="Dropout Risk")
    st.plotly_chart(fig6, use_container_width=True)
