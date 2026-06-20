"""SSIP — Academic Intelligence"""
import streamlit as st, pandas as pd, plotly.express as px, plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, PAGE_HEADER, RISK_COLORS

st.set_page_config(page_title="SSIP | Academic Intelligence", layout="wide")
PAGE_HEADER("📚 Academic Intelligence", "Subject performance, study habits, and academic trends")

df = load_data()

col_f1, col_f2 = st.columns(2)
with col_f1:
    class_sel = st.multiselect("Class", sorted(df["class_level"].unique()), default=sorted(df["class_level"].unique()))
with col_f2:
    gender_sel = st.multiselect("Gender", list(df["gender"].unique()), default=list(df["gender"].unique()))
df_f = df[df["class_level"].isin(class_sel) & df["gender"].isin(gender_sel)]

# ── KPIs ──────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Avg Score",       f"{df_f['average_score'].mean():.1f}")
c2.metric("Avg Math",        f"{df_f['math_score'].mean():.1f}")
c3.metric("Avg English",     f"{df_f['english_score'].mean():.1f}")
c4.metric("Avg Science",     f"{df_f['science_score'].mean():.1f}")
c5.metric("Avg Social Std",  f"{df_f['social_studies_score'].mean():.1f}")
st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("#### Subject Averages by Class")
    subj_by_class = df_f.groupby("class_level")[
        ["math_score","english_score","science_score","social_studies_score"]
    ].mean().round(1).reset_index()
    subj_by_class.columns = ["Class","Mathematics","English","Science","Social Studies"]
    class_order = ["JSS1","JSS2","JSS3","SS1","SS2","SS3"]
    subj_by_class["Class"] = pd.Categorical(subj_by_class["Class"], class_order, ordered=True)
    subj_by_class = subj_by_class.sort_values("Class")
    fig = go.Figure()
    colors = ["#3b82f6","#10b981","#f59e0b","#8b5cf6"]
    for subj, color in zip(["Mathematics","English","Science","Social Studies"], colors):
        fig.add_trace(go.Scatter(x=subj_by_class["Class"], y=subj_by_class[subj],
                                 mode="lines+markers", name=subj, line=dict(color=color, width=2),
                                 marker=dict(size=7)))
    fig.add_hline(y=50, line_dash="dash", line_color="#dc2626", opacity=0.6)
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                      height=320, margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b",
                      xaxis_title="Class", yaxis_title="Average Score")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Score Distribution by Subject")
    long_df = df_f[["math_score","english_score","science_score","social_studies_score"]].melt(
        var_name="Subject", value_name="Score")
    long_df["Subject"] = long_df["Subject"].str.replace("_score","").str.replace("_"," ").str.title()
    fig2 = px.box(long_df, x="Subject", y="Score", color="Subject",
                  color_discrete_sequence=["#3b82f6","#10b981","#f59e0b","#8b5cf6"])
    fig2.add_hline(y=50, line_dash="dash", line_color="#dc2626", opacity=0.6)
    fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=320, margin=dict(t=10,b=10,l=10,r=10), showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("#### Hardest Subject (Student-Perceived)")
    hs = df_f["hardest_subject"].value_counts().reset_index()
    hs.columns = ["Subject","Count"]
    fig3 = px.pie(hs, values="Count", names="Subject", hole=0.5,
                  color_discrete_sequence=["#dc2626","#ea580c","#d97706","#3b82f6"])
    fig3.update_layout(paper_bgcolor="#0f172a", font_color="#e2e8f0",
                       height=300, margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b")
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown("#### Score Trend Distribution by Class")
    trend_data = df_f.groupby(["class_level","score_trend"]).size().reset_index(name="Count")
    trend_data["class_level"] = pd.Categorical(trend_data["class_level"], class_order, ordered=True)
    fig4 = px.bar(trend_data.sort_values("class_level"), x="class_level", y="Count",
                  color="score_trend", barmode="group",
                  color_discrete_map={"Improving":"#16a34a","Stable":"#3b82f6","Declining":"#dc2626"})
    fig4.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=300, margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b",
                       xaxis_title="Class", yaxis_title="Students")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("#### 📖 Study Habits vs Performance")
col_e, col_f_ = st.columns(2)
with col_e:
    sh_order = ["<1hr","1-2hrs","3-4hrs",">4hrs"]
    sh_avg = df_f.groupby("study_hours_per_day")["average_score"].mean().reindex(sh_order).reset_index()
    fig5 = px.bar(sh_avg, x="study_hours_per_day", y="average_score",
                  color="average_score", color_continuous_scale=["#dc2626","#16a34a"],
                  range_color=[45,75], text_auto=".1f", title="Avg Score by Study Hours")
    fig5.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=280, margin=dict(t=30,b=10,l=10,r=10), coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

with col_f_:
    ac_order = ["Below 50%","50-70%","71-90%","Above 90%"]
    ac_avg = df_f.groupby("assignment_completion_rate")["average_score"].mean().reindex(ac_order).reset_index()
    fig6 = px.bar(ac_avg, x="assignment_completion_rate", y="average_score",
                  color="average_score", color_continuous_scale=["#dc2626","#16a34a"],
                  range_color=[40,80], text_auto=".1f", title="Avg Score by Assignment Completion")
    fig6.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=280, margin=dict(t=30,b=10,l=10,r=10), coloraxis_showscale=False)
    st.plotly_chart(fig6, use_container_width=True)

# WAEC section
st.markdown("---")
st.markdown("#### 🎓 WAEC Readiness (SS Students Only)")
ss_df = df_f[df_f["is_senior_student"]==1]
if len(ss_df) > 0:
    cw1, cw2, cw3 = st.columns(3)
    cw1.metric("SS Students",   len(ss_df))
    cw2.metric("Avg Mock Score", f"{ss_df['mock_exam_score'].mean():.1f}")
    cw3.metric("Avg WRI",        f"{ss_df['WRI'].mean():.1f}")
    ep_counts = ss_df["exam_preparation_level"].value_counts().reset_index()
    ep_order  = ["Very Poor","Poor","Fair","Good","Excellent"]
    ep_counts.columns = ["Level","Count"]
    ep_counts["Level"] = pd.Categorical(ep_counts["Level"], ep_order, ordered=True)
    fig7 = px.bar(ep_counts.sort_values("Level"), x="Level", y="Count",
                  color="Level",
                  color_discrete_map={"Very Poor":"#dc2626","Poor":"#ea580c","Fair":"#d97706",
                                      "Good":"#16a34a","Excellent":"#22c55e"})
    fig7.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=280, margin=dict(t=10,b=10,l=10,r=10), showlegend=False,
                       title="WAEC Exam Preparation Levels")
    st.plotly_chart(fig7, use_container_width=True)
