"""
AI Resume Analyzer & ATS Scoring System
Main Streamlit Application
"""

import streamlit as st
import os
import plotly.graph_objects as go
from dotenv import load_dotenv

from utils.parser import extract_text_from_pdf, validate_pdf
from utils.analyzer import configure_client, analyze_resume, match_job_description
from utils.report_generator import generate_pdf_report

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv()

# ── CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

/* ── Root Tokens ───────────────────────────────────────── */
:root {
  --ink:        #0D1117;
  --ink-soft:   #3D4552;
  --ink-mute:   #6B7280;
  --surface:    #FFFFFF;
  --surface-2:  #F6F8FA;
  --surface-3:  #EEF2F7;
  --accent:     #1B4FD8;
  --accent-dim: #EBF0FD;
  --accent-2:   #0E9E6B;
  --accent-2-dim:#E6F7F2;
  --warn:       #B45309;
  --warn-dim:   #FEF3C7;
  --danger:     #B91C1C;
  --danger-dim: #FEE2E2;
  --border:     #D8DEE9;
  --border-soft:#E8ECF2;
  --radius-sm:  8px;
  --radius:     12px;
  --radius-lg:  18px;
  --shadow-sm:  0 1px 3px rgba(13,17,23,0.08);
  --shadow:     0 4px 16px rgba(13,17,23,0.10);
  --shadow-lg:  0 8px 28px rgba(13,17,23,0.13);
}

/* ── Reset ─────────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
}

/* Hide sidebar toggle & default padding */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.main .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── App shell ─────────────────────────────────────────── */
.stApp {
  background: var(--surface-2);
}

/* ── Top bar ───────────────────────────────────────────── */
.topbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 2.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
.topbar-logo {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
}
.topbar-logo span { color: var(--accent); }
.topbar-badge {
  font-size: 0.72rem;
  font-weight: 600;
  background: var(--accent-dim);
  color: var(--accent);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* ── Hero ──────────────────────────────────────────────── */
.hero {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 3.5rem 2.5rem 3rem;
  text-align: center;
}
.hero-eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
  margin-bottom: 0.75rem;
}
.hero h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(2rem, 4.5vw, 3.25rem);
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 0.75rem;
}
.hero h1 em {
  font-style: normal;
  color: var(--accent);
}
.hero p {
  color: var(--ink-mute);
  font-size: clamp(0.95rem, 1.8vw, 1.1rem);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ── Main content wrapper ──────────────────────────────── */
.content-wrap {
  max-width: 1080px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

/* ── Cards ─────────────────────────────────────────────── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1rem;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.card:hover {
  box-shadow: var(--shadow);
  border-color: #C5CCDB;
}
.card-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--ink);
  margin-bottom: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ── Score label ───────────────────────────────────────── */
.score-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--ink-mute);
  text-align: center;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-top: 0.15rem;
}

/* ── Tags ──────────────────────────────────────────────── */
.tag-cloud { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag {
  padding: 0.28rem 0.8rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid;
}
.tag-tech   { background: var(--accent-dim);   color: var(--accent);  border-color: #BFCFFA; }
.tag-soft   { background: var(--accent-2-dim); color: #065F46;        border-color: #A7DEC9; }
.tag-miss   { background: var(--danger-dim);   color: var(--danger);  border-color: #FBBABA; }
.tag-kw     { background: var(--warn-dim);     color: var(--warn);    border-color: #FBBF24; }
.tag-match  { background: var(--accent-2-dim); color: #065F46;        border-color: #A7DEC9; }

/* ── List items ────────────────────────────────────────── */
.list-item {
  padding: 0.6rem 0.875rem;
  border-radius: var(--radius-sm);
  margin-bottom: 0.35rem;
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--ink);
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  line-height: 1.55;
  border-left: 3px solid;
}
.list-item.strength   { background: var(--accent-2-dim); border-color: var(--accent-2); }
.list-item.weakness   { background: var(--warn-dim);     border-color: #D97706; }
.list-item.suggestion { background: var(--accent-dim);   border-color: var(--accent); }
.list-item.career     { background: var(--surface-3);    border-color: #94A3B8; }

/* ── ATS probability badge ─────────────────────────────── */
.prob-badge {
  display: inline-block;
  padding: 0.45rem 1.25rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.02em;
}
.prob-high   { background: var(--accent-2-dim); color: #065F46; border: 1.5px solid var(--accent-2); }
.prob-medium { background: var(--warn-dim);     color: #92400E; border: 1.5px solid #D97706; }
.prob-low    { background: var(--danger-dim);   color: var(--danger); border: 1.5px solid #DC2626; }

/* ── Section header ────────────────────────────────────── */
.section-header {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--ink);
  margin: 2rem 0 1rem;
  letter-spacing: -0.01em;
}

/* ── Upload zone ───────────────────────────────────────── */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--border) !important;
  border-radius: var(--radius) !important;
  background: var(--surface-2) !important;
  padding: 0.75rem !important;
  transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
}

/* ── Buttons ───────────────────────────────────────────── */
.stButton > button {
  width: 100%;
  background: var(--accent) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.75rem 2rem !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  letter-spacing: 0.01em;
  transition: background 0.15s, transform 0.1s !important;
  box-shadow: 0 1px 4px rgba(27,79,216,0.25) !important;
}
.stButton > button:hover {
  background: #163DB8 !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}

/* ── Download button ───────────────────────────────────── */
.stDownloadButton > button {
  background: var(--accent-2) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 4px rgba(14,158,107,0.25) !important;
}
.stDownloadButton > button:hover {
  background: #0A7A52 !important;
}

/* ── Tabs ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  gap: 0.25rem;
  background: var(--surface);
  border-radius: var(--radius-sm);
  padding: 0.3rem;
  border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--ink-soft);
  padding: 0.45rem 1rem;
}
.stTabs [aria-selected="true"] {
  background: var(--accent) !important;
  color: white !important;
}

/* ── Metrics ───────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--surface);
  border-radius: var(--radius-sm);
  padding: 1rem;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

/* ── Text area ─────────────────────────────────────────── */
.stTextArea textarea {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.875rem !important;
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--ink) !important;
  background: var(--surface-2) !important;
}
.stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(27,79,216,0.12) !important;
}

/* ── Alert overrides ───────────────────────────────────── */
.stAlert {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  font-size: 0.875rem !important;
}

/* ── Mobile responsive ─────────────────────────────────── */
@media (max-width: 768px) {
  .topbar { padding: 0.65rem 1rem; }
  .hero   { padding: 2rem 1rem 1.5rem; }
  .content-wrap { padding: 1.25rem 0.75rem 3rem; }
  .card   { padding: 1rem; }
  .stButton > button { font-size: 0.875rem !important; }
}

/* ── Divider ───────────────────────────────────────────── */
.divider {
  height: 1px;
  background: var(--border-soft);
  margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

load_dotenv()

# ── API key — loaded from env, no manual input needed ───────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Prefer Groq if available, fall back to Gemini
if GROQ_API_KEY:
    API_KEY  = GROQ_API_KEY
    PROVIDER = "groq"
elif GEMINI_API_KEY:
    API_KEY  = GEMINI_API_KEY
    PROVIDER = "gemini"
else:
    API_KEY  = ""
    PROVIDER = "groq"


# ── Helper functions ────────────────────────────────────────
def score_color(score: int) -> str:
    if score >= 80:
        return "#0E9E6B"
    elif score >= 60:
        return "#D97706"
    elif score >= 40:
        return "#F97316"
    return "#B91C1C"


def gauge_chart(value: int, title: str, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 12, "family": "DM Sans", "color": "#6B7280"}},
        number={"suffix": "", "font": {"size": 32, "family": "Space Grotesk", "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#D8DEE9",
                     "tickfont": {"size": 9, "color": "#9CA3AF"}},
            "bar": {"color": color, "thickness": 0.22},
            "bgcolor": "#F6F8FA",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40],  "color": "#FEE2E2"},
                {"range": [40, 70],  "color": "#FEF3C7"},
                {"range": [70, 100], "color": "#D1FAE5"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        height=195,
        margin=dict(l=20, r=20, t=32, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans"},
    )
    return fig


def radar_chart(categories, values):
    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(27,79,216,0.12)",
        line=dict(color="#1B4FD8", width=2),
        marker=dict(color="#1B4FD8", size=5),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10],
                            tickfont=dict(size=8, color="#9CA3AF"),
                            gridcolor="#E8ECF2"),
            angularaxis=dict(tickfont=dict(size=10, family="DM Sans", color="#3D4552"),
                             gridcolor="#E8ECF2"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        height=260,
        margin=dict(l=28, r=28, t=28, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def tags_html(items, css_class):
    return '<div class="tag-cloud">' + "".join(
        f'<span class="tag {css_class}">{item}</span>' for item in items
    ) + "</div>"


def list_items_html(items, css_class, icon):
    return "".join(
        f'<div class="list-item {css_class}"><span>{icon}</span><span>{item}</span></div>'
        for item in items
    )


# ── Session state ───────────────────────────────────────────
for key, val in {
    "analysis": None, "match_data": None,
    "resume_text": None, "analyzed": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Top bar ─────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-logo">Resume<span>IQ</span></div>
  <div class="topbar-badge">✦ AI-Powered</div>
</div>
""", unsafe_allow_html=True)


# ── Hero ────────────────────────────────────────────────────
provider_label = "Groq" if PROVIDER == "Wajid Khan" else "Wajid Khan"
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">Developed by {provider_label}</div>
  <h1>Your resume, <em>analyzed</em>.</h1>
  <p>Get an instant ATS score, skills-gap breakdown, and actionable recommendations — in seconds.</p>
</div>
""", unsafe_allow_html=True)


# ── No API key warning ──────────────────────────────────────
if not API_KEY:
    st.warning(
        "⚠️ No API key found. Set `GROQ_API_KEY` or `GEMINI_API_KEY` in your `.env` file and restart the app.",
        icon="🔑",
    )


# ── Input panel ─────────────────────────────────────────────
st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

col_upload, col_jd = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown('<div class="card-title">📄 Resume (PDF)</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Drop your PDF here",
        type=["pdf"],
        help="PDF up to 10 MB",
        label_visibility="collapsed",
    )
    if uploaded_file:
        validation = validate_pdf(uploaded_file)
        if validation["valid"]:
            st.success(f"✅ **{uploaded_file.name}** — {uploaded_file.size / 1024:.1f} KB")
        else:
            st.error(f"❌ {validation['error']}")
            uploaded_file = None
    st.markdown("</div>", unsafe_allow_html=True)

with col_jd:
    st.markdown('<div class="card-title">🎯 Job Description (Optional)</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste job description",
        height=158,
        placeholder="Paste a job posting to get match score and keyword gap analysis…",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ── Analyze button ───────────────────────────────────────────
_, btn_col, _ = st.columns([1.5, 2, 1.5])
with btn_col:
    analyze_clicked = st.button("Analyze Resume →", use_container_width=True, disabled=not API_KEY)

if analyze_clicked:
    if not uploaded_file:
        st.error("❌ Please upload a PDF resume.")
    else:
        uploaded_file.seek(0)
        validation = validate_pdf(uploaded_file)
        if not validation["valid"]:
            st.error(f"❌ {validation['error']}")
        else:
            with st.spinner("Extracting resume text…"):
                uploaded_file.seek(0)
                parse_result = extract_text_from_pdf(uploaded_file)

            if not parse_result["success"]:
                st.error(f"❌ {parse_result['error']}")
            else:
                st.success(f"✅ {parse_result['pages']} page(s) extracted.")
                st.session_state.resume_text = parse_result["text"]
                try:
                    model = configure_client(API_KEY, PROVIDER)

                    with st.spinner("Analyzing your resume…"):
                        analysis = analyze_resume(model, parse_result["text"], PROVIDER)
                    st.session_state.analysis = analysis

                    if job_description.strip():
                        with st.spinner("Matching against job description…"):
                            match_data = match_job_description(
                                model, parse_result["text"], job_description, PROVIDER
                            )
                        st.session_state.match_data = match_data
                    else:
                        st.session_state.match_data = None

                    st.session_state.analyzed = True
                    st.balloons()

                except RuntimeError as e:
                    st.error(f"❌ AI Error: {e}")


# ── Results ──────────────────────────────────────────────────
if st.session_state.analyzed and st.session_state.analysis:
    analysis   = st.session_state.analysis
    match_data = st.session_state.match_data

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    candidate = analysis.get("candidate_name", "Candidate")
    target    = analysis.get("job_title_target", "")
    subtitle  = f" — {target}" if target else ""
    st.markdown(f'<div class="section-header">📊 Results for {candidate}{subtitle}</div>',
                unsafe_allow_html=True)

    # Gauge row
    resume_score = analysis.get("resume_score", 0)
    ats_score    = analysis.get("ats_score",    0)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(gauge_chart(resume_score, "Resume Score", score_color(resume_score)),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="score-label">Overall Quality</div>', unsafe_allow_html=True)
    with g2:
        st.plotly_chart(gauge_chart(ats_score, "ATS Score", score_color(ats_score)),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="score-label">ATS Compatibility</div>', unsafe_allow_html=True)
    with g3:
        if match_data:
            mp = match_data.get("match_percentage", 0)
            st.plotly_chart(gauge_chart(mp, "Job Match", score_color(mp)),
                            use_container_width=True, config={"displayModeBar": False})
            st.markdown('<div class="score-label">Job Description Match</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:2.5rem 1rem;height:200px;
                 display:flex;flex-direction:column;justify-content:center;align-items:center;">
              <div style="font-size:1.75rem;margin-bottom:0.5rem;">🎯</div>
              <div style="font-size:0.82rem;font-weight:500;color:#6B7280;line-height:1.5;">
                Paste a job description<br>for a match score
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(["🛠 Skills", "📝 Summary", "💡 Suggestions", "🎯 Job Match", "📄 Resume Text"])

    # ── TAB 1: Skills ─────────────────────────────────────
    with tabs[0]:
        s1, s2 = st.columns(2)
        with s1:
            tech = analysis.get("technical_skills", [])
            st.markdown('<div class="card"><div class="card-title">⚙️ Technical Skills</div>', unsafe_allow_html=True)
            st.markdown(tags_html(tech, "tag-tech") if tech else "<p style='color:#6B7280;font-size:0.875rem'>None detected.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            soft = analysis.get("soft_skills", [])
            st.markdown('<div class="card"><div class="card-title">🤝 Soft Skills</div>', unsafe_allow_html=True)
            st.markdown(tags_html(soft, "tag-soft") if soft else "<p style='color:#6B7280;font-size:0.875rem'>None detected.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with s2:
            missing = analysis.get("missing_skills", [])
            st.markdown('<div class="card"><div class="card-title">❌ Missing Skills</div>', unsafe_allow_html=True)
            if missing:
                st.markdown(tags_html(missing, "tag-miss"), unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#0E9E6B;font-size:0.875rem;font-weight:500'>No critical gaps found.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            categories = ["Technical", "Communication", "Leadership", "Problem Solving", "ATS Fit"]
            t = min(len(tech), 10)
            so = min(len(soft), 10)
            radar_vals = [
                min(t * 1.2, 10), min(so * 1.5, 10),
                min(so * 0.8, 10), min(t * 0.9, 10),
                min(ats_score / 10, 10),
            ]
            st.plotly_chart(radar_chart(categories, radar_vals),
                            use_container_width=True, config={"displayModeBar": False})

    # ── TAB 2: Summary ────────────────────────────────────
    with tabs[1]:
        if analysis.get("professional_summary"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✨ AI Professional Summary</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#3D4552;line-height:1.7;font-size:0.9rem'>{analysis['professional_summary']}</p>",
                        unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            for icon, label, key in [
                ("💼", "Experience", "experience_summary"),
                ("📁", "Projects",   "projects_summary"),
            ]:
                st.markdown(f'<div class="card"><div class="card-title">{icon} {label}</div>'
                            f'<p style="color:#3D4552;font-size:0.875rem;line-height:1.65">'
                            f'{analysis.get(key, "N/A")}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card"><div class="card-title">🎓 Education</div>'
                        f'<p style="color:#3D4552;font-size:0.875rem;line-height:1.65">'
                        f'{analysis.get("education_summary", "N/A")}</p></div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">💪 Strengths</div>', unsafe_allow_html=True)
            st.markdown(list_items_html(analysis.get("strengths", []), "strength", "✓"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">⚠️ Areas for Improvement</div>', unsafe_allow_html=True)
        st.markdown(list_items_html(analysis.get("weaknesses", []), "weakness", "→"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 3: Suggestions ───────────────────────────────
    with tabs[2]:
        r1, r2 = st.columns(2)
        with r1:
            st.markdown('<div class="card"><div class="card-title">💡 Resume Improvements</div>', unsafe_allow_html=True)
            st.markdown(list_items_html(analysis.get("improvement_suggestions", []), "suggestion", "→"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">🔗 LinkedIn Tips</div>', unsafe_allow_html=True)
            st.markdown(list_items_html(analysis.get("linkedin_suggestions", []), "career", "→"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with r2:
            st.markdown('<div class="card"><div class="card-title">🚀 Career Recommendations</div>', unsafe_allow_html=True)
            st.markdown(list_items_html(analysis.get("career_recommendations", []), "career", "→"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">🎤 Interview Tips</div>', unsafe_allow_html=True)
            st.markdown(list_items_html(analysis.get("interview_tips", []), "suggestion", "→"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        kw = analysis.get("keyword_highlights", [])
        if kw:
            st.markdown('<div class="card"><div class="card-title">🔑 Keyword Highlights</div>', unsafe_allow_html=True)
            st.markdown(tags_html(kw, "tag-kw"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 4: Job Match ─────────────────────────────────
    with tabs[3]:
        if not match_data:
            st.info("Paste a job description above and re-run the analysis to see your match score.")
        else:
            mp   = match_data.get("match_percentage", 0)
            ma   = match_data.get("ats_score", 0)
            prob = match_data.get("ats_pass_probability", "Unknown")
            prob_class = {"High": "prob-high", "Medium": "prob-medium"}.get(prob, "prob-low")

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.plotly_chart(gauge_chart(mp, "Match %", score_color(mp)),
                                use_container_width=True, config={"displayModeBar": False})
            with mc2:
                st.plotly_chart(gauge_chart(ma, "ATS Score", score_color(ma)),
                                use_container_width=True, config={"displayModeBar": False})
            with mc3:
                st.markdown(f"""
                <div class="card" style="text-align:center;padding:2rem 1rem;">
                  <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.06em;
                              text-transform:uppercase;color:#6B7280;margin-bottom:0.6rem;">
                    ATS Pass Probability
                  </div>
                  <div class="prob-badge {prob_class}">{prob}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
              <div class="card-title">🧠 Role Fit Summary</div>
              <p style="color:#3D4552;line-height:1.7;font-size:0.9rem">
                {match_data.get("role_fit_summary", "")}
              </p>
            </div>
            """, unsafe_allow_html=True)

            j1, j2 = st.columns(2)
            with j1:
                st.markdown('<div class="card"><div class="card-title">✅ Matched Keywords</div>', unsafe_allow_html=True)
                st.markdown(tags_html(match_data.get("matched_keywords", []), "tag-match"), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="card"><div class="card-title">❌ Missing Keywords</div>', unsafe_allow_html=True)
                st.markdown(tags_html(match_data.get("missing_keywords", []), "tag-miss"), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with j2:
                st.markdown('<div class="card"><div class="card-title">🛠 Missing Skills</div>', unsafe_allow_html=True)
                st.markdown(tags_html(match_data.get("missing_skills", []), "tag-miss"), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="card"><div class="card-title">✏️ Tailoring Tips</div>', unsafe_allow_html=True)
                st.markdown(list_items_html(match_data.get("tailoring_tips", []), "suggestion", "→"), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            rec = match_data.get("recommended_improvements", [])
            if rec:
                st.markdown('<div class="card"><div class="card-title">💡 Recommended Improvements</div>', unsafe_allow_html=True)
                st.markdown(list_items_html(rec, "career", "→"), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 5: Resume Text ────────────────────────────────
    with tabs[4]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📄 Extracted Text</div>', unsafe_allow_html=True)
        st.text_area("Resume", value=st.session_state.resume_text or "",
                     height=400, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📥 Download Report</div>', unsafe_allow_html=True)
    _, dl_col, _ = st.columns([1.5, 2, 1.5])
    with dl_col:
        with st.spinner("Building PDF report…"):
            try:
                pdf_bytes = generate_pdf_report(analysis, match_data)
                name = analysis.get("candidate_name", "Candidate").replace(" ", "_")
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{name}_Resume_Analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"PDF generation failed: {e}")

st.markdown("</div>", unsafe_allow_html=True)  # close content-wrap
st.markdown("<br><br>", unsafe_allow_html=True)
