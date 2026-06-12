"""
Report Generator
Creates a downloadable PDF report from the resume analysis results.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime


# Brand colors
PRIMARY = colors.HexColor("#6C63FF")
SECONDARY = colors.HexColor("#0EA5E9")
SUCCESS = colors.HexColor("#10B981")
WARNING = colors.HexColor("#F59E0B")
DANGER = colors.HexColor("#EF4444")
DARK = colors.HexColor("#1E1B4B")
LIGHT_BG = colors.HexColor("#F8F7FF")


def generate_pdf_report(analysis: dict, match_data: dict = None) -> bytes:
    """
    Generate a professional PDF report from analysis results.

    Args:
        analysis: Resume analysis dict from Gemini
        match_data: Optional job match dict from Gemini

    Returns:
        PDF as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=DARK,
        spaceBefore=16,
        spaceAfter=8,
        fontName="Helvetica-Bold",
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
        leading=15,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=16,
        bulletIndent=6,
    )

    # ── Header ──────────────────────────────────────────────
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    candidate = analysis.get("candidate_name", "Candidate")
    story.append(Paragraph(f"Candidate: {candidate}", subtitle_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=12))

    # ── Score Cards ──────────────────────────────────────────
    story.append(Paragraph("📊 Score Summary", section_style))

    resume_score = analysis.get("resume_score", 0)
    ats_score = analysis.get("ats_score", 0)

    score_data = [
        ["Metric", "Score", "Rating"],
        ["Resume Quality Score", f"{resume_score}/100", _rating_label(resume_score)],
        ["ATS Compatibility Score", f"{ats_score}/100", _rating_label(ats_score)],
    ]
    if match_data:
        match_pct = match_data.get("match_percentage", 0)
        score_data.append(["Job Match Percentage", f"{match_pct}%", _rating_label(match_pct)])

    score_table = Table(score_data, colWidths=[7 * cm, 4 * cm, 5 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("ROWHEIGHT", (0, 0), (-1, -1), 24),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # ── Professional Summary ────────────────────────────────
    if analysis.get("professional_summary"):
        story.append(Paragraph("✨ AI-Generated Professional Summary", section_style))
        story.append(Paragraph(analysis["professional_summary"], body_style))

    # ── Skills ──────────────────────────────────────────────
    story.append(Paragraph("🛠 Skills Identified", section_style))

    tech_skills = ", ".join(analysis.get("technical_skills", [])) or "None identified"
    soft_skills = ", ".join(analysis.get("soft_skills", [])) or "None identified"

    skills_data = [
        ["Technical Skills", tech_skills],
        ["Soft Skills", soft_skills],
    ]
    skills_table = Table(skills_data, colWidths=[5 * cm, 11 * cm])
    skills_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWHEIGHT", (0, 0), (-1, -1), 30),
        ("WORDWRAP", (1, 0), (1, -1), True),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 8))

    # ── Experience & Education ──────────────────────────────
    for section_title, key in [
        ("💼 Experience Summary", "experience_summary"),
        ("🎓 Education Summary", "education_summary"),
        ("📁 Projects Summary", "projects_summary"),
    ]:
        val = analysis.get(key, "Not provided.")
        story.append(Paragraph(section_title, section_style))
        story.append(Paragraph(val, body_style))

    # ── Strengths & Weaknesses ──────────────────────────────
    story.append(Paragraph("💪 Strengths", section_style))
    for item in analysis.get("strengths", []):
        story.append(Paragraph(f"• {item}", bullet_style))

    story.append(Paragraph("⚠️ Areas for Improvement", section_style))
    for item in analysis.get("weaknesses", []):
        story.append(Paragraph(f"• {item}", bullet_style))

    # ── Missing Skills ──────────────────────────────────────
    story.append(Paragraph("❌ Missing Skills Checklist", section_style))
    for skill in analysis.get("missing_skills", []):
        story.append(Paragraph(f"☐  {skill}", bullet_style))

    # ── Suggestions ─────────────────────────────────────────
    story.append(Paragraph("💡 Resume Improvement Suggestions", section_style))
    for item in analysis.get("improvement_suggestions", []):
        story.append(Paragraph(f"→  {item}", bullet_style))

    # ── Career Recommendations ──────────────────────────────
    story.append(Paragraph("🚀 Career Recommendations", section_style))
    for item in analysis.get("career_recommendations", []):
        story.append(Paragraph(f"→  {item}", bullet_style))

    # ── Interview Tips ──────────────────────────────────────
    if analysis.get("interview_tips"):
        story.append(Paragraph("🎤 Interview Preparation Tips", section_style))
        for tip in analysis["interview_tips"]:
            story.append(Paragraph(f"• {tip}", bullet_style))

    # ── Job Match Section ────────────────────────────────────
    if match_data:
        story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceBefore=16, spaceAfter=8))
        story.append(Paragraph("🎯 Job Description Match Analysis", section_style))

        story.append(Paragraph(
            f"<b>ATS Pass Probability:</b> {match_data.get('ats_pass_probability', 'N/A')}",
            body_style,
        ))
        story.append(Paragraph(
            f"<b>Role Fit Summary:</b> {match_data.get('role_fit_summary', '')}",
            body_style,
        ))

        story.append(Paragraph("Matched Keywords:", section_style))
        for kw in match_data.get("matched_keywords", []):
            story.append(Paragraph(f"✓  {kw}", bullet_style))

        story.append(Paragraph("Missing Keywords:", section_style))
        for kw in match_data.get("missing_keywords", []):
            story.append(Paragraph(f"☐  {kw}", bullet_style))

        story.append(Paragraph("Tailoring Tips:", section_style))
        for tip in match_data.get("tailoring_tips", []):
            story.append(Paragraph(f"→  {tip}", bullet_style))

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")))
    story.append(Paragraph(
        "Generated by AI Resume Analyzer · Powered by Google Gemini",
        subtitle_style,
    ))

    doc.build(story)
    return buffer.getvalue()


def _rating_label(score: int) -> str:
    """Return a qualitative label for a numeric score."""
    if score >= 85:
        return "Excellent ✅"
    elif score >= 70:
        return "Good 👍"
    elif score >= 50:
        return "Fair ⚠️"
    else:
        return "Needs Work ❌"
