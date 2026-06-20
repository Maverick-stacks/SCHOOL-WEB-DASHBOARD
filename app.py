"""
============================================================
STUDENT SUCCESS INTELLIGENCE PLATFORM (SSIP)
Main Streamlit Application
============================================================
Run: streamlit run app.py
============================================================
"""
import streamlit as st

st.set_page_config(
    page_title="SSIP — Student Success Intelligence Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────
st.markdown("""
<style>
  /* Sidebar */
  [data-testid="stSidebar"] { background: #0f172a; }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #3b82f6;
  }
  [data-testid="metric-container"] label { color: #94a3b8 !important; font-size:0.8rem; }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important; font-size: 1.8rem; font-weight: 700;
  }

  /* Page header */
  .ssip-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    padding: 24px 32px; border-radius: 16px; margin-bottom: 24px;
    border: 1px solid #334155;
  }
  .ssip-header h1 { color: #f1f5f9; margin: 0; font-size: 1.8rem; font-weight: 800; }
  .ssip-header p  { color: #94a3b8; margin: 6px 0 0 0; font-size: 0.95rem; }

  /* Risk badges */
  .badge-critical { background:#dc2626; color:white; padding:4px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }
  .badge-high     { background:#ea580c; color:white; padding:4px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }
  .badge-medium   { background:#d97706; color:white; padding:4px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }
  .badge-low      { background:#16a34a; color:white; padding:4px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }

  /* Cards */
  .info-card {
    background: #1e293b; border-radius: 12px; padding: 20px;
    border: 1px solid #334155; margin: 8px 0;
  }
  .warning-card {
    background: #1c1917; border-radius: 12px; padding: 20px;
    border-left: 4px solid #dc2626; margin: 8px 0;
  }
  .success-card {
    background: #052e16; border-radius: 12px; padding: 20px;
    border-left: 4px solid #16a34a; margin: 8px 0;
  }
  .ssip-divider { border: none; border-top: 1px solid #334155; margin: 20px 0; }
  h2, h3 { color: #e2e8f0 !important; }
  p, li  { color: #94a3b8; }
  .stDataFrame { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 SSIP")
    st.markdown("**Student Success Intelligence Platform**")
    st.markdown("*Turning data into early intervention*")
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown("🏠  **Home**")
   st.page_link("pages/01_executive_overview.py",  label="📊  Executive Overview")
   st.page_link("pages/02_early_warning.py",       label="🚨  Early Warning Center")
   st.page_link("pages/03_student_explorer.py",    label="🔍  Student Explorer")
   st.page_link("pages/04_academic_intel.py",      label="📚  Academic Intelligence")
   st.page_link("pages/05_wellbeing.py",           label="💚  Wellbeing Intelligence")
   st.page_link("pages/06_predictive.py",          label="🤖  Predictive Analytics")
   st.page_link("pages/07_segmentation.py",        label="🗂️  Student Segmentation")
   st.page_link("pages/08_scenario_simulator.py",  label="⚙️  Scenario Simulator")
   st.page_link("pages/09_recommendations.py",     label="💡  Recommendation Center")
    st.markdown("---")
    st.caption("Built by odianosen | AltSchool Africa")
    st.caption("Data Science Portfolio Project")

# ── Home page ─────────────────────────────────────────────
st.markdown("""
<div class="ssip-header">
  <h1>🎓 Student Success Intelligence Platform</h1>
  <p>AI-powered educational analytics and early intervention system for Nigerian secondary schools</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3,2])
with col1:
    st.markdown("### The Problem Schools Face Today")
    st.markdown("""
    <div class="warning-card">
      <p>📌 A student starts missing classes.</p>
      <p>📌 Assignments are submitted late — then not at all.</p>
      <p>📌 Scores decline quietly over one term.</p>
      <p>📌 The teacher notices. <strong style='color:#f87171'>After the damage is done.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What SSIP Changes")
    st.markdown("""
    <div class="success-card">
      <p>✅ <strong style='color:#4ade80'>Early Warning Center</strong> — flags at-risk students before failure occurs</p>
      <p>✅ <strong style='color:#4ade80'>Student Explorer</strong> — reveals the <em>why</em> behind every risk score</p>
      <p>✅ <strong style='color:#4ade80'>Scenario Simulator</strong> — shows what happens if the school intervenes</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Platform at a Glance")
    st.markdown("""
    | Layer | Answers |
    |-------|---------|
    | 📊 Descriptive | What is happening? |
    | 🔍 Diagnostic | Why is it happening? |
    | 🤖 Predictive | What will happen? |
    | 💡 Prescriptive | What should we do? |
    """)
    st.markdown("### 9 Custom Intelligence Indices")
    indices = [
        ("SSI","Student Success Index"),
        ("EI", "Engagement Index"),
        ("PSI","Parent Support Index"),
        ("RAI","Resource Accessibility Index"),
        ("WBI","Wellbeing Index"),
        ("ARI","Academic Resilience Index"),
        ("WRI","WAEC Readiness Index"),
        ("SNI","Support Need Index"),
        ("DVI","Dropout Vulnerability Index"),
    ]
    for code, name in indices:
        st.markdown(f"**`{code}`** — {name}")

st.markdown("---")
st.info("👈 Use the sidebar to navigate to any section of the platform.")
