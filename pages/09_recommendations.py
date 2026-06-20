"""SSIP — Recommendation Center"""
import streamlit as st, pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, PAGE_HEADER, RISK_COLORS

st.set_page_config(page_title="SSIP | Recommendations", layout="wide")
PAGE_HEADER("💡 Recommendation Center",
            "Prescriptive analytics — not just what's happening, but what the school should do")

df = load_data()

st.markdown("""
<div style="background:#1e293b;border-radius:12px;padding:16px 22px;border:1px solid #334155;margin-bottom:20px;">
  <p style="color:#94a3b8;margin:0;">
    SSIP doesn't just surface problems — it recommends actions.
    Each intervention below is triggered by data patterns across the student population.
  </p>
</div>""", unsafe_allow_html=True)

# ── Priority Interventions ────────────────────────────────
st.markdown("### 🚨 Priority Interventions Required")

interventions = [
    {
        "priority":"CRITICAL", "color":"#dc2626",
        "icon":"🔴", "title":"Immediate Academic Support",
        "count": (df["average_score"] < 50).sum(),
        "metric": f"{(df['average_score'] < 50).mean()*100:.1f}% of students",
        "trigger":"Average score below pass threshold (50)",
        "actions":["After-school tutoring in Mathematics and Science",
                   "Weekly progress review with form teacher",
                   "Supplemental instruction materials",
                   "Peer study group pairing with stronger students"]
    },
    {
        "priority":"CRITICAL","color":"#dc2626",
        "icon":"🔴","title":"Attendance Recovery Programme",
        "count": (df["attendance_rate"] < 65).sum(),
        "metric": f"{(df['attendance_rate'] < 65).mean()*100:.1f}% of students",
        "trigger":"Attendance rate below 65%",
        "actions":["Individual attendance recovery contract",
                   "Parent/guardian notification and meeting",
                   "Transport support assessment",
                   "Bi-weekly check-ins with form teacher"]
    },
    {
        "priority":"HIGH","color":"#ea580c",
        "icon":"🟠","title":"Financial Aid Referrals",
        "count": (df["financial_stress_level"].isin(["Very High","High"])).sum(),
        "metric": f"{(df['financial_stress_level'].isin(['Very High','High'])).mean()*100:.1f}% of students",
        "trigger":"Very High or High financial stress",
        "actions":["Referral to school bursary office",
                   "Flexible tuition payment plan discussion",
                   "Scholarship eligibility screening",
                   "State/NGO educational grant applications"]
    },
    {
        "priority":"HIGH","color":"#ea580c",
        "icon":"🟠","title":"Mental Health & Counseling",
        "count": (df["stress_level"].isin(["Very High","High"])).sum(),
        "metric": f"{(df['stress_level'].isin(['Very High','High'])).mean()*100:.1f}% of students",
        "trigger":"High or Very High stress level",
        "actions":["Scheduled counselor session",
                   "Wellbeing check-in with form teacher",
                   "Workload review and possible adjustment",
                   "Peer support group for SS3 exam stress"]
    },
    {
        "priority":"MEDIUM","color":"#d97706",
        "icon":"🟡","title":"Parent Engagement Programme",
        "count": (df["parent_involvement"].isin(["Very Low","Low"])).sum(),
        "metric": f"{(df['parent_involvement'].isin(['Very Low','Low'])).mean()*100:.1f}% of students",
        "trigger":"Low or Very Low parent involvement",
        "actions":["Formal parent-teacher meeting request",
                   "PTA awareness and outreach",
                   "Monthly academic progress SMS/call updates",
                   "Home visit for unresponsive guardians"]
    },
    {
        "priority":"MEDIUM","color":"#d97706",
        "icon":"🟡","title":"Digital Access Support",
        "count": (df["internet_access_quality"].isin(["No Access","Very Poor"])).sum(),
        "metric": f"{(df['internet_access_quality'].isin(['No Access','Very Poor'])).mean()*100:.1f}% of students",
        "trigger":"No access or very poor internet quality",
        "actions":["Extended computer lab access hours",
                   "Printed study materials and past questions",
                   "School WiFi access policy review",
                   "Partnership with telco for subsidised data"]
    },
    {
        "priority":"LOW","color":"#16a34a",
        "icon":"🟢","title":"WAEC Readiness Support",
        "count": (df[(df["is_senior_student"]==1)]["exam_preparation_level"]
                  .isin(["Very Poor","Poor"])).sum(),
        "metric": "SS students with poor exam prep",
        "trigger":"Poor or Very Poor WAEC preparation (SS students)",
        "actions":["Intensive revision timetable",
                   "Mock examination programme",
                   "Past question practice sessions",
                   "Subject-specific revision camps"]
    },
]

for iv in interventions:
    with st.expander(f"{iv['icon']} {iv['title']} — {iv['count']} students affected", expanded=iv["priority"]=="CRITICAL"):
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown(f"""
            <div style="background:#1e293b;border-radius:10px;padding:16px;border-left:4px solid {iv['color']};">
              <p style="color:#94a3b8;margin:0;font-size:0.75rem;">PRIORITY</p>
              <p style="color:{iv['color']};font-weight:800;font-size:1.1rem;margin:4px 0;">{iv['priority']}</p>
              <p style="color:#e2e8f0;font-size:1.6rem;font-weight:800;margin:8px 0 4px 0;">{iv['count']}</p>
              <p style="color:#94a3b8;font-size:0.8rem;margin:0;">{iv['metric']}</p>
              <hr style="border-color:#334155;margin:10px 0;">
              <p style="color:#64748b;font-size:0.75rem;margin:0;font-style:italic;">Trigger: {iv['trigger']}</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("**Recommended Actions:**")
            for action in iv["actions"]:
                st.markdown(f"✅ {action}")

# ── Population-level recommendations ─────────────────────
st.markdown("---")
st.markdown("### 📊 School-Wide Strategic Recommendations")

strategic = [
    ("📡","Infrastructure","31% of students have very poor or no internet access. "
     "Prioritise school-based WiFi or printed learning materials as a bridge solution."),
    ("🍽️","Nutrition","Significant portion of Low-SES students report eating 1 meal per day. "
     "Consider partnering with NGOs for a school feeding programme."),
    ("📉","SS3 Pressure","SS3 students show the highest stress levels school-wide. "
     "Introduce structured WAEC counseling from SS2 to reduce last-minute pressure."),
    ("👨‍👩‍👧","Guardian Diversity","13% of students live with guardians or relatives, "
     "and 4% are orphans/wards — these groups carry 2× the dropout risk. "
     "Create a dedicated welfare follow-up system for these students."),
    ("📚","Mathematics Gap","Mathematics is the hardest subject for the largest number of students. "
     "Introduce peer-tutoring and supplemental instruction targeting maths specifically."),
    ("🏠","Home Study Environment","40% of students rate their home study environment as Poor or Very Poor. "
     "Extend library hours and study hall access after school."),
]

for icon, title, text in strategic:
    st.markdown(f"""
    <div style="background:#1e293b;border-radius:10px;padding:14px 20px;margin:8px 0;
         border:1px solid #334155;">
      <strong style="color:#e2e8f0;">{icon} {title}</strong>
      <p style="color:#94a3b8;margin:6px 0 0 0;font-size:0.87rem;">{text}</p>
    </div>""", unsafe_allow_html=True)
