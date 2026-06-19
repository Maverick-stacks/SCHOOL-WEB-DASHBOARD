"""Shared utilities for SSIP dashboard pages."""
import pandas as pd
import numpy as np
import streamlit as st
import joblib, os

import pathlib
_DASHBOARD_DIR = pathlib.Path(__file__).parent
BASE           = _DASHBOARD_DIR.parent
DATA_PATH      = str(BASE / "data" / "processed" / "student_success_processed.csv")
MODELS_PATH    = str(BASE / "models")

RISK_COLORS = {
    "Critical": "#dc2626", "High": "#ea580c",
    "Medium": "#d97706",   "Low": "#16a34a"
}
RISK_ORDER  = ["Critical", "High", "Medium", "Low"]
DROPOUT_ORDER = ["High", "Medium", "Low"]

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

@st.cache_resource
def load_model(name):
    path = os.path.join(MODELS_PATH, name)
    if os.path.exists(path):
        return joblib.load(path)
    return None

def risk_badge(risk):
    colors = {"Critical":"#dc2626","High":"#ea580c","Medium":"#d97706","Low":"#16a34a"}
    c = colors.get(risk, "#64748b")
    return f'<span style="background:{c};color:white;padding:3px 10px;border-radius:12px;font-size:0.78rem;font-weight:700;">{risk}</span>'

def metric_card(title, value, delta=None, color="#3b82f6"):
    delta_html = f'<p style="color:#94a3b8;margin:4px 0 0 0;font-size:0.8rem;">{delta}</p>' if delta else ""
    return f"""
    <div style="background:#1e293b;border-radius:12px;padding:20px;
                border-left:4px solid {color};margin:4px 0;">
      <p style="color:#94a3b8;margin:0;font-size:0.78rem;text-transform:uppercase;
                letter-spacing:0.08em;">{title}</p>
      <p style="color:#f1f5f9;margin:6px 0 0 0;font-size:1.9rem;font-weight:800;">{value}</p>
      {delta_html}
    </div>"""

def index_gauge(name, value, description=""):
    color = "#16a34a" if value>=70 else "#d97706" if value>=50 else "#dc2626"
    bar_w = min(int(value), 100)
    return f"""
    <div style="background:#1e293b;border-radius:10px;padding:14px 18px;margin:6px 0;border:1px solid #334155;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="color:#e2e8f0;font-weight:600;font-size:0.88rem;">{name}</span>
        <span style="color:{color};font-weight:700;font-size:1rem;">{value:.1f}</span>
      </div>
      <div style="background:#334155;border-radius:6px;height:8px;overflow:hidden;">
        <div style="width:{bar_w}%;background:{color};height:100%;border-radius:6px;
                    transition:width 0.4s ease;"></div>
      </div>
      {f'<p style="color:#64748b;font-size:0.72rem;margin:5px 0 0 0;">{description}</p>' if description else ''}
    </div>"""

PAGE_HEADER = lambda title, subtitle: st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
     padding:22px 28px;border-radius:14px;margin-bottom:22px;border:1px solid #334155;">
  <h1 style="color:#f1f5f9;margin:0;font-size:1.65rem;font-weight:800;">{title}</h1>
  <p style="color:#94a3b8;margin:6px 0 0 0;font-size:0.9rem;">{subtitle}</p>
</div>""", unsafe_allow_html=True)
