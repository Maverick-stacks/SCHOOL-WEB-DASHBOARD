"""SSIP — Wellbeing Intelligence"""
import streamlit as st, pandas as pd, plotly.express as px, plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, PAGE_HEADER

st.set_page_config(page_title="SSIP | Wellbeing Intelligence", layout="wide")
PAGE_HEADER("💚 Wellbeing Intelligence", "Student mental health, stress, motivation and satisfaction insights")

df = load_data()

class_sel = st.multiselect("Class Level", sorted(df["class_level"].unique()), default=sorted(df["class_level"].unique()))
df_f = df[df["class_level"].isin(class_sel)]

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg WBI Score",    f"{df_f['WBI'].mean():.1f}/100")
c2.metric("High Stress",      f"{(df_f['stress_level'].isin(['High','Very High'])).sum()}")
c3.metric("Poor Mental Health",f"{(df_f['mental_health_indicator']=='Poor').sum()}")
c4.metric("Avg Sleep",         f"{df_f['sleep_hours_per_night'].mean():.1f} hrs")
st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("#### Stress Level by Class")
    stress_order = ["Very Low","Low","Moderate","High","Very High"]
    stress_data  = df_f.groupby(["class_level","stress_level"]).size().reset_index(name="Count")
    class_order  = ["JSS1","JSS2","JSS3","SS1","SS2","SS3"]
    stress_data["class_level"] = pd.Categorical(stress_data["class_level"], class_order, ordered=True)
    fig = px.bar(stress_data.sort_values("class_level"), x="class_level", y="Count",
                 color="stress_level", barmode="stack",
                 color_discrete_map={"Very High":"#dc2626","High":"#ea580c",
                                     "Moderate":"#d97706","Low":"#16a34a","Very Low":"#22c55e"},
                 category_orders={"stress_level": stress_order})
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                      height=320, margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Sleep Hours Distribution")
    fig2 = px.histogram(df_f, x="sleep_hours_per_night", nbins=20,
                        color_discrete_sequence=["#8b5cf6"])
    fig2.add_vline(x=8, line_dash="dash", line_color="#16a34a",
                   annotation_text="Recommended (8hrs)", annotation_font_color="#16a34a")
    fig2.add_vline(x=df_f["sleep_hours_per_night"].mean(), line_dash="dot", line_color="#d97706",
                   annotation_text=f"Mean {df_f['sleep_hours_per_night'].mean():.1f}hrs",
                   annotation_font_color="#d97706")
    fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=320, margin=dict(t=10,b=10,l=10,r=10))
    st.plotly_chart(fig2, use_container_width=True)

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("#### Stress Level vs Average Score")
    stress_score = df_f.groupby("stress_level").agg(
        avg_score=("average_score","mean"),
        count=("student_id","count")
    ).reindex(stress_order).reset_index()
    fig3 = px.bar(stress_score, x="stress_level", y="avg_score",
                  color="avg_score", color_continuous_scale=["#16a34a","#dc2626"],
                  range_color=[40,70], text_auto=".1f")
    fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=300, margin=dict(t=10,b=10,l=10,r=10), coloraxis_showscale=False,
                       xaxis_title="Stress Level", yaxis_title="Avg Score")
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown("#### Motivation Level vs Average Score")
    mot_order = ["Very Low","Low","Moderate","High","Very High"]
    mot_score = df_f.groupby("motivation_level")["average_score"].mean().reindex(mot_order).reset_index()
    fig4 = px.bar(mot_score, x="motivation_level", y="average_score",
                  color="average_score", color_continuous_scale=["#dc2626","#16a34a"],
                  range_color=[40,70], text_auto=".1f")
    fig4.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=300, margin=dict(t=10,b=10,l=10,r=10), coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("#### 🗣️ Student Voice — Top Challenges")
if "primary_challenge" in df_f.columns:
    keywords = {"Internet":["internet"],"Electricity":["electricity","power","nepa"],
                "Mathematics":["mathematics","math"],"Finance":["financial","fees","money"],
                "Workload":["workload","assignment","homework"],
                "Health":["health","sick"],"Transport":["transport","distance","commute"],
                "Family":["family","responsibilities"],"Mental Health":["stress","mental","fatigue"],
                "Study Materials":["textbook","materials","books"]}
    kw_counts = {k: df_f["primary_challenge"].str.lower().str.contains("|".join(v)).sum()
                 for k,v in keywords.items()}
    kw_df = pd.DataFrame(list(kw_counts.items()), columns=["Challenge","Students Affected"])
    kw_df = kw_df.sort_values("Students Affected", ascending=True)
    fig5 = px.bar(kw_df, x="Students Affected", y="Challenge", orientation="h",
                  color="Students Affected", color_continuous_scale=["#1e3a5f","#dc2626"],
                  text_auto=True)
    fig5.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=360, margin=dict(t=10,b=10,l=10,r=10), coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)
