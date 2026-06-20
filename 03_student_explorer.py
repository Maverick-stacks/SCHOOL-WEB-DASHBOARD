"""SSIP — Student Explorer ⭐ WOW Feature #2"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, PAGE_HEADER, RISK_COLORS, index_gauge, risk_badge

st.set_page_config(page_title="SSIP | Student Explorer", layout="wide")
PAGE_HEADER("🔍 Student Explorer",
            "Deep dive into any student — understand not just who is at risk, but why")

df = load_data()

# ── Student selector ──────────────────────────────────────
col_s1, col_s2, col_s3 = st.columns([2,1,1])
with col_s1:
    search = st.text_input("🔎 Search by Student ID or keyword", placeholder="e.g. STU_0042")
with col_s2:
    class_sel = st.selectbox("Filter by Class", ["All"] + sorted(df["class_level"].unique()))
with col_s3:
    risk_sel = st.selectbox("Filter by Risk", ["All","Critical","High","Medium","Low"])

filtered = df.copy()
if search:
    filtered = filtered[filtered["student_id"].str.contains(search, case=False, na=False)]
if class_sel != "All":
    filtered = filtered[filtered["class_level"] == class_sel]
if risk_sel != "All":
    filtered = filtered[filtered["risk_level"] == risk_sel]

risk_sort = {"Critical":4,"High":3,"Medium":2,"Low":1}
filtered["_rsort"] = filtered["risk_level"].map(risk_sort)
filtered = filtered.sort_values("_rsort", ascending=False)

student_list = filtered["student_id"].tolist()
if not student_list:
    st.warning("No students match your filters."); st.stop()

selected_id = st.selectbox("Select Student", student_list)
s = df[df["student_id"] == selected_id].iloc[0]

# ── Header card ───────────────────────────────────────────
risk_color = RISK_COLORS.get(s["risk_level"], "#64748b")
drop_color = {"High":"#dc2626","Medium":"#d97706","Low":"#16a34a"}.get(s["dropout_risk"],"#64748b")
pf_color   = "#16a34a" if s["pass_fail"]=="Pass" else "#dc2626"
trend_icon = "📈" if s["score_trend"]=="Improving" else "📉" if s["score_trend"]=="Declining" else "➡️"

st.markdown(f"""
<div style="background:#1e293b;border-radius:16px;padding:24px 32px;
     border:1px solid #334155;margin-bottom:20px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
    <div>
      <h2 style="color:#f1f5f9;margin:0;font-size:1.6rem;">{s['student_id']}</h2>
      <p style="color:#94a3b8;margin:6px 0 0 0;">
        {s['class_level']} &nbsp;|&nbsp; {s['gender']} &nbsp;|&nbsp;
        Age Group: {s['age_group']} &nbsp;|&nbsp; {s['boarding_status']}
      </p>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;">
      <span style="background:{risk_color};color:white;padding:6px 14px;border-radius:20px;
            font-weight:700;font-size:0.85rem;">Risk: {s['risk_level']}</span>
      <span style="background:{drop_color};color:white;padding:6px 14px;border-radius:20px;
            font-weight:700;font-size:0.85rem;">Dropout: {s['dropout_risk']}</span>
      <span style="background:{pf_color};color:white;padding:6px 14px;border-radius:20px;
            font-weight:700;font-size:0.85rem;">{s['pass_fail']}</span>
      <span style="background:#334155;color:#e2e8f0;padding:6px 14px;border-radius:20px;
            font-weight:600;font-size:0.85rem;">{trend_icon} {s['score_trend']}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 4-column snapshot ─────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
c1.metric("Average Score",    f"{s['average_score']:.1f}",
          f"Prev: {s['prev_average_score']:.1f}")
c2.metric("Attendance Rate",  f"{s['attendance_rate']:.1f}%")
c3.metric("Study Hours/Day",  str(s["study_hours_per_day"]))
c4.metric("Counselor Visits", str(int(s["counselor_visits_per_term"])))

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Intelligence Indices", "📚 Academic Profile",
    "💚 Wellbeing", "👨‍👩‍👧 Family & Resources", "💡 Recommendations"
])

# TAB 1 — INDICES ──────────────────────────────────────────
with tab1:
    st.markdown("#### Student Intelligence Indices vs School Average")
    indices = ["SSI","EI","PSI","RAI","WBI","ARI","WRI","SNI","DVI"]
    idx_labels = {
        "SSI":"Student Success","EI":"Engagement","PSI":"Parent Support",
        "RAI":"Resource Access","WBI":"Wellbeing","ARI":"Academic Resilience",
        "WRI":"WAEC Readiness","SNI":"Support Need","DVI":"Dropout Vulnerability"
    }
    idx_descriptions = {
        "SSI":"Academic output + consistent effort",
        "EI": "Active school involvement beyond academics",
        "PSI":"Parental involvement and home environment",
        "RAI":"Internet, electricity, device, distance",
        "WBI":"Stress, sleep, mental health, motivation",
        "ARI":"Improvement trend and persistence",
        "WRI":"WAEC exam preparedness (SS students)",
        "SNI":"Composite institutional support need",
        "DVI":"Composite dropout vulnerability",
    }
    col_l, col_r = st.columns(2)
    for i, idx in enumerate(indices):
        student_val = s[idx] if idx in s.index else 0
        school_avg  = df[idx].mean()
        delta = student_val - school_avg
        delta_str = f"School avg: {school_avg:.1f} (Δ {delta:+.1f})"
        gauge_html = index_gauge(f"{idx} — {idx_labels[idx]}", student_val, delta_str)
        if i % 2 == 0:
            col_l.markdown(gauge_html, unsafe_allow_html=True)
        else:
            col_r.markdown(gauge_html, unsafe_allow_html=True)

    st.markdown("#### Radar Chart — Student vs School Average")
    radar_indices = ["SSI","EI","PSI","RAI","WBI","ARI"]
    student_vals  = [s[i] for i in radar_indices]
    school_vals   = [df[i].mean() for i in radar_indices]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=student_vals+[student_vals[0]],
                                   theta=radar_indices+[radar_indices[0]],
                                   fill="toself", name=selected_id,
                                   line_color="#3b82f6", fillcolor="rgba(59,130,246,0.2)"))
    fig.add_trace(go.Scatterpolar(r=school_vals+[school_vals[0]],
                                   theta=radar_indices+[radar_indices[0]],
                                   fill="toself", name="School Average",
                                   line_color="#94a3b8", fillcolor="rgba(148,163,184,0.1)"))
    fig.update_layout(polar=dict(bgcolor="#1e293b",
                                  radialaxis=dict(visible=True,range=[0,100],
                                                  color="#64748b",gridcolor="#334155"),
                                  angularaxis=dict(color="#94a3b8")),
                      paper_bgcolor="#0f172a", font_color="#e2e8f0",
                      legend_bgcolor="#1e293b", height=380,
                      margin=dict(t=20,b=20,l=40,r=40))
    st.plotly_chart(fig, use_container_width=True)

# TAB 2 — ACADEMIC ─────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Current vs Previous Term Scores")
        subjects = ["Mathematics","English","Science","Social Studies"]
        current  = [s["math_score"],s["english_score"],s["science_score"],s["social_studies_score"]]
        previous = [s["prev_math_score"],s["prev_english_score"],
                    s["prev_science_score"],s["prev_social_studies_score"]]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Current Term", x=subjects, y=current,
                              marker_color="#3b82f6", text=[f"{v:.0f}" for v in current],
                              textposition="outside", textfont_color="#e2e8f0"))
        fig2.add_trace(go.Bar(name="Previous Term", x=subjects, y=previous,
                              marker_color="#64748b", text=[f"{v:.0f}" for v in previous],
                              textposition="outside", textfont_color="#e2e8f0"))
        fig2.add_hline(y=50, line_dash="dash", line_color="#dc2626",
                       annotation_text="Pass line", annotation_font_color="#dc2626")
        fig2.update_layout(barmode="group", paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                           font_color="#e2e8f0", height=340,
                           margin=dict(t=10,b=10,l=10,r=10), legend_bgcolor="#1e293b")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("#### Academic Behaviour Profile")
        behaviours = {
            "Assignment Completion": s["assignment_completion_rate"],
            "Homework Consistency":  s["homework_submission_consistency"],
            "Study Hours/Day":       s["study_hours_per_day"],
            "Participation Level":   s["participation_level"],
            "Library Usage":         s["library_usage"],
            "Peer Collaboration":    s["peer_collaboration"],
        }
        for label, val in behaviours.items():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                 padding:10px 14px;background:#1e293b;border-radius:8px;margin:4px 0;
                 border:1px solid #334155;">
              <span style="color:#94a3b8;font-size:0.85rem;">{label}</span>
              <span style="color:#e2e8f0;font-weight:600;font-size:0.88rem;">{val}</span>
            </div>""", unsafe_allow_html=True)

        if s.get("is_senior_student") == 1:
            st.markdown("#### 🎓 WAEC Readiness")
            st.info(f"Exam Prep: **{s['exam_preparation_level']}** | "
                    f"Mock Score: **{s.get('mock_exam_score','N/A')}** | "
                    f"Subjects: **{int(s.get('waec_subject_count', 0)) if s.get('waec_subject_count') else 'N/A'}**")

# TAB 3 — WELLBEING ────────────────────────────────────────
with tab3:
    col_w1, col_w2 = st.columns(2)
    wellbeing_data = {
        "Stress Level":        s["stress_level"],
        "Sleep Hours/Night":   f"{s['sleep_hours_per_night']:.1f} hrs",
        "Mental Health":       s["mental_health_indicator"],
        "Exam Anxiety":        s["exam_anxiety_level"],
        "Motivation Level":    s["motivation_level"],
        "Peer Relationships":  s["peer_relationship_quality"],
        "School Satisfaction": s["school_satisfaction"],
    }
    stress_colors = {"Very High":"#dc2626","High":"#ea580c","Moderate":"#d97706",
                     "Low":"#16a34a","Very Low":"#22c55e"}

    with col_w1:
        st.markdown("#### Wellbeing Snapshot")
        for label, val in wellbeing_data.items():
            color = stress_colors.get(str(val), "#94a3b8")
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                 padding:10px 16px;background:#1e293b;border-radius:8px;margin:4px 0;">
              <span style="color:#94a3b8;font-size:0.85rem;">{label}</span>
              <span style="color:{color};font-weight:700;font-size:0.88rem;">{val}</span>
            </div>""", unsafe_allow_html=True)

    with col_w2:
        st.markdown("#### Student Voice")
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:12px;padding:20px;border:1px solid #334155;">
          <p style="color:#94a3b8;font-size:0.78rem;text-transform:uppercase;
               letter-spacing:0.08em;margin:0 0 10px 0;">Primary Challenge</p>
          <p style="color:#f1f5f9;font-size:0.95rem;margin:0 0 18px 0;">
            "{s.get('primary_challenge','Not provided')}"</p>
          <p style="color:#94a3b8;font-size:0.78rem;text-transform:uppercase;
               letter-spacing:0.08em;margin:0 0 10px 0;">Support Needed</p>
          <p style="color:#f1f5f9;font-size:0.95rem;margin:0;">
            "{s.get('support_needed','Not provided')}"</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"**WBI Score:** {s['WBI']:.1f} / 100")
        st.progress(int(s['WBI']))

# TAB 4 — FAMILY & RESOURCES ──────────────────────────────
with tab4:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("#### Family Background")
        fam = {
            "Guardian Type":        s["guardian_type"],
            "Socioeconomic Status": s["socioeconomic_status"],
            "Parent Education":     s["parent_education_level"],
            "Parent Involvement":   s["parent_involvement"],
            "Meeting Attendance":   s["parent_meeting_attendance"],
            "Home Study Env.":      s["home_study_environment"],
            "No. of Siblings":      str(int(s["number_of_siblings"])),
            "Scholarship":          s["receives_scholarship"],
        }
        for label, val in fam.items():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:9px 14px;
                 background:#1e293b;border-radius:8px;margin:4px 0;">
              <span style="color:#94a3b8;font-size:0.84rem;">{label}</span>
              <span style="color:#e2e8f0;font-weight:600;font-size:0.84rem;">{val}</span>
            </div>""", unsafe_allow_html=True)

    with col_f2:
        st.markdown("#### Resources & Infrastructure")
        res = {
            "Internet Access":      s["internet_access_quality"],
            "Personal Device":      s["has_personal_device"],
            "Electricity":          s["electricity_reliability"],
            "Distance to School":   f"{s['distance_from_school_km']:.1f} km",
            "Commute Time":         f"{int(s['commute_time_minutes'])} min",
            "Transport Mode":       s["transport_mode"],
            "Financial Stress":     s["financial_stress_level"],
            "Tuition Status":       s["tuition_payment_status"],
            "Meals/Day":            str(int(s["meals_per_day"])),
            "Part-time Job":        s["has_part_time_job"],
        }
        poor_vals = {"No Access","Very Poor","Very Unreliable","Unreliable",
                     "Very High","Outstanding","No"}
        for label, val in res.items():
            color = "#fca5a5" if str(val) in poor_vals else \
                    "#86efac" if str(val) in {"Yes","Good","Excellent","Reliable","Very Reliable","Paid"} \
                    else "#e2e8f0"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:9px 14px;
                 background:#1e293b;border-radius:8px;margin:4px 0;">
              <span style="color:#94a3b8;font-size:0.84rem;">{label}</span>
              <span style="color:{color};font-weight:600;font-size:0.84rem;">{val}</span>
            </div>""", unsafe_allow_html=True)

# TAB 5 — RECOMMENDATIONS ─────────────────────────────────
with tab5:
    st.markdown("#### 💡 AI-Generated Intervention Recommendations")
    st.markdown(f"*Based on {selected_id}'s full profile — risk level: **{s['risk_level']}***")

    recs = []
    if s["attendance_rate"] < 65:
        recs.append(("🔴","Attendance Recovery Plan",
                     f"Attendance at {s['attendance_rate']:.1f}% is critically low. "
                     "Recommend: weekly attendance contract, parent/guardian notification, "
                     "transport support if distance is a barrier."))
    if s["average_score"] < 50:
        recs.append(("🔴","Immediate Academic Support",
                     f"Average score {s['average_score']:.1f} is below pass threshold. "
                     "Recommend: after-school tutoring, supplemental instruction in "
                     f"{s.get('hardest_subject','Mathematics')}."))
    if s["stress_level"] in ["Very High","High"]:
        recs.append(("🟠","Counseling Session",
                     f"Stress level is {s['stress_level']}. "
                     "Recommend: schedule counselor appointment, wellbeing check-in, "
                     "review workload with form teacher."))
    if s["financial_stress_level"] in ["Very High","High"]:
        recs.append(("🟠","Financial Aid Review",
                     f"Financial stress is {s['financial_stress_level']}. "
                     "Recommend: refer to bursary office, explore scholarship eligibility, "
                     "discuss flexible payment plan."))
    if s["parent_involvement"] in ["Very Low","Low"]:
        recs.append(("🟡","Parent Engagement",
                     "Low parental involvement detected. "
                     "Recommend: formal parent-teacher meeting, PTA outreach, "
                     "home visit if unresponsive."))
    if s["score_trend"] == "Declining":
        recs.append(("🟡","Performance Monitoring",
                     f"Score declined from {s['prev_average_score']:.1f} to {s['average_score']:.1f}. "
                     "Recommend: bi-weekly progress review with subject teachers, "
                     "early intervention before end-of-term exams."))
    if s["internet_access_quality"] in ["No Access","Very Poor"]:
        recs.append(("🟡","Digital Access Support",
                     "Limited internet access may hinder learning. "
                     "Recommend: school computer lab access, printed study materials."))
    if s["motivation_level"] in ["Very Low","Low"]:
        recs.append(("🟢","Motivation & Mentorship",
                     "Low motivation detected. "
                     "Recommend: peer mentorship programme, career counseling, "
                     "recognition of any improvements."))
    if s.get("is_senior_student")==1 and s["exam_preparation_level"] in ["Very Poor","Poor"]:
        recs.append(("🔴","WAEC Exam Preparation",
                     f"Exam preparation is {s['exam_preparation_level']}. "
                     "Recommend: intensive revision schedule, past question practice, "
                     "study group with higher-performing peers."))

    if not recs:
        st.success("✅ No critical interventions required. Continue monitoring.")
    else:
        for icon, title, desc in recs:
            priority_color = {"🔴":"#dc2626","🟠":"#ea580c",
                              "🟡":"#d97706","🟢":"#16a34a"}.get(icon,"#64748b")
            st.markdown(f"""
            <div style="background:#1e293b;border-radius:10px;padding:16px 20px;
                 margin:8px 0;border-left:4px solid {priority_color};">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <span style="font-size:1.2rem;">{icon}</span>
                <strong style="color:#e2e8f0;font-size:0.95rem;">{title}</strong>
              </div>
              <p style="color:#94a3b8;margin:0;font-size:0.85rem;">{desc}</p>
            </div>""", unsafe_allow_html=True)
