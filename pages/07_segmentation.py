"""SSIP — Student Segmentation"""
import streamlit as st, pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, PAGE_HEADER

st.set_page_config(page_title="SSIP | Segmentation", layout="wide")
PAGE_HEADER("🗂️ Student Segmentation",
            "K-Means clustering — automatically groups students into meaningful personas")

df = load_data()

SEGMENT_FEATURES = ["SSI","EI","PSI","RAI","WBI","ARI","DVI","SNI",
                     "attendance_rate","average_score"]
SEGMENT_FEATURES = [f for f in SEGMENT_FEATURES if f in df.columns]

@st.cache_data
def run_kmeans(n_clusters=4):
    X = df[SEGMENT_FEATURES].fillna(df[SEGMENT_FEATURES].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    return labels, X_scaled

st.sidebar.markdown("#### Clustering Settings")
n_clusters = st.sidebar.slider("Number of Segments", 2, 6, 4)

labels, X_scaled = run_kmeans(n_clusters)
df_seg = df.copy()
df_seg["segment"] = labels

# ── Auto-name segments by profile ────────────────────────
seg_profiles = df_seg.groupby("segment")[
    ["SSI","WBI","DVI","average_score","attendance_rate"]
].mean().round(1)

segment_names = {}
for seg in seg_profiles.index:
    p = seg_profiles.loc[seg]
    if p["SSI"] > 65 and p["WBI"] > 60:
        segment_names[seg] = f"🟢 Segment {seg+1}: Thriving Students"
    elif p["SSI"] > 55 and p["DVI"] < 40:
        segment_names[seg] = f"🔵 Segment {seg+1}: Stable Performers"
    elif p["SSI"] < 50 and p["DVI"] > 50:
        segment_names[seg] = f"🔴 Segment {seg+1}: High-Risk Students"
    else:
        segment_names[seg] = f"🟡 Segment {seg+1}: Silent Strugglers"

df_seg["segment_name"] = df_seg["segment"].map(segment_names)

# ── Segment KPIs ─────────────────────────────────────────
st.markdown("### Segment Overview")
seg_summary = df_seg.groupby("segment_name").agg(
    Students=("student_id","count"),
    Avg_Score=("average_score","mean"),
    Avg_Attendance=("attendance_rate","mean"),
    Pass_Rate=("pass_fail", lambda x: (x=="Pass").mean()*100),
    Avg_SSI=("SSI","mean"),
    Avg_DVI=("DVI","mean"),
    Avg_WBI=("WBI","mean"),
).round(1).reset_index()
seg_summary.columns = ["Segment","Students","Avg Score","Avg Attendance (%)","Pass Rate (%)","SSI","DVI","WBI"]
st.dataframe(seg_summary, use_container_width=True, hide_index=True)

st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("#### Segment Distribution")
    seg_counts = df_seg["segment_name"].value_counts().reset_index()
    seg_counts.columns = ["Segment","Count"]
    fig = px.pie(seg_counts, values="Count", names="Segment", hole=0.45,
                 color_discrete_sequence=["#16a34a","#3b82f6","#dc2626","#d97706"])
    fig.update_layout(paper_bgcolor="#0f172a", font_color="#e2e8f0",
                      height=320, legend_bgcolor="#1e293b", margin=dict(t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### SSI vs DVI by Segment")
    fig2 = px.scatter(df_seg.sample(min(600, len(df_seg)), random_state=42),
                      x="SSI", y="DVI", color="segment_name", opacity=0.75,
                      hover_data=["student_id","average_score","attendance_rate"],
                      color_discrete_sequence=["#16a34a","#3b82f6","#dc2626","#d97706","#8b5cf6","#f97316"])
    fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                       height=320, legend_bgcolor="#1e293b", margin=dict(t=10,b=10,l=10,r=10),
                       xaxis_title="SSI (Success)", yaxis_title="DVI (Dropout Vulnerability)")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown("#### Index Profiles by Segment")
indices_to_plot = ["SSI","EI","PSI","RAI","WBI","ARI"]
seg_radar = df_seg.groupby("segment_name")[indices_to_plot].mean().reset_index()
fig3 = go.Figure()
colors_radar = ["#16a34a","#3b82f6","#dc2626","#d97706","#8b5cf6","#f97316"]
for i, row in seg_radar.iterrows():
    vals = [row[idx] for idx in indices_to_plot]
    fig3.add_trace(go.Scatterpolar(
        r=vals+[vals[0]], theta=indices_to_plot+[indices_to_plot[0]],
        fill="toself", name=row["segment_name"],
        line_color=colors_radar[i % len(colors_radar)],
        fillcolor=colors_radar[i % len(colors_radar)].replace("#","rgba(") + ",0.15)"
        if False else colors_radar[i % len(colors_radar)],
        opacity=0.8
    ))
fig3.update_layout(polar=dict(bgcolor="#1e293b",
                               radialaxis=dict(visible=True, range=[0,100], color="#64748b",
                                               gridcolor="#334155"),
                               angularaxis=dict(color="#94a3b8")),
                   paper_bgcolor="#0f172a", font_color="#e2e8f0",
                   legend_bgcolor="#1e293b", height=420, margin=dict(t=20,b=20))
st.plotly_chart(fig3, use_container_width=True)

# ── Segment deep-dive ─────────────────────────────────────
st.markdown("---")
selected_seg = st.selectbox("🔍 Explore a Segment", sorted(df_seg["segment_name"].unique()))
seg_students = df_seg[df_seg["segment_name"]==selected_seg]
st.markdown(f"**{len(seg_students)} students** in this segment")
show_cols = ["student_id","class_level","gender","average_score","attendance_rate",
             "risk_level","dropout_risk","pass_fail","SSI","DVI","WBI"]
st.dataframe(seg_students[[c for c in show_cols if c in seg_students.columns]
                           ].head(50), use_container_width=True, hide_index=True)
