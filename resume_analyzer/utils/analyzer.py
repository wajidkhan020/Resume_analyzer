"""
AI Resume Analyzer
Supports both Groq (free) and Google Gemini API.
"""

import json
import re


def configure_client(api_key: str, provider: str = "groq"):
    """Configure and return AI client."""
    if provider == "groq":
        from groq import Groq
        return Groq(api_key=api_key)
    else:
        from google import genai
        return genai.Client(api_key=api_key)


def _call_groq(client, prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(client, prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()


def _parse_json(raw: str) -> dict:
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


def analyze_resume(client, resume_text: str, provider: str = "groq") -> dict:
    prompt = f"""
You are an expert HR professional, ATS specialist, and career coach with 15+ years of experience.

Analyze the following resume and return a JSON object ONLY — no explanation, no markdown, no backticks.

Resume Text:
\"\"\"
{resume_text}
\"\"\"

Return ONLY this exact JSON structure with no other text:
{{
  "resume_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "candidate_name": "<name or Unknown>",
  "job_title_target": "<likely target role>",
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "education_summary": "<2-3 sentence summary>",
  "experience_summary": "<2-3 sentence summary>",
  "projects_summary": "<1-2 sentence summary>",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "missing_skills": ["skill1", "skill2", "skill3", "skill4"],
  "career_recommendations": ["rec1", "rec2", "rec3"],
  "improvement_suggestions": ["s1", "s2", "s3", "s4"],
  "professional_summary": "<2-3 sentence AI-generated summary>",
  "interview_tips": ["tip1", "tip2", "tip3"],
  "linkedin_suggestions": ["s1", "s2"],
  "keyword_highlights": ["kw1", "kw2", "kw3", "kw4", "kw5"]
}}
"""
    try:
        if provider == "groq":
            raw = _call_groq(client, prompt)
        else:
            raw = _call_gemini(client, prompt)
        return _parse_json(raw)
    except json.JSONDecodeError:
        return _fallback_analysis()
    except Exception as e:
        raise RuntimeError(f"{str(e)}")


def match_job_description(client, resume_text: str, job_description: str, provider: str = "groq") -> dict:
    prompt = f"""
You are an expert ATS system and HR recruiter.

Compare the resume against the job description and return ONLY a JSON object — no markdown, no backticks.

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"

Return ONLY this exact JSON with no other text:
{{
  "match_percentage": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "missing_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
  "missing_skills": ["skill1", "skill2", "skill3"],
  "matched_keywords": ["kw1", "kw2", "kw3"],
  "ats_pass_probability": "<Low or Medium or High>",
  "recommended_improvements": ["i1", "i2", "i3"],
  "tailoring_tips": ["tip1", "tip2", "tip3"],
  "role_fit_summary": "<2-3 sentence assessment>"
}}
"""
    try:
        if provider == "groq":
            raw = _call_groq(client, prompt)
        else:
            raw = _call_gemini(client, prompt)
        return _parse_json(raw)
    except json.JSONDecodeError:
        return _fallback_match()
    except Exception as e:
        raise RuntimeError(f"{str(e)}")


def _fallback_analysis() -> dict:
    return {
        "resume_score": 0, "ats_score": 0,
        "candidate_name": "Unknown", "job_title_target": "Unknown",
        "technical_skills": [], "soft_skills": [],
        "education_summary": "Could not parse.", "experience_summary": "Could not parse.",
        "projects_summary": "Could not parse.", "strengths": [], "weaknesses": [],
        "missing_skills": [], "career_recommendations": [],
        "improvement_suggestions": ["Please re-upload and try again."],
        "professional_summary": "", "interview_tips": [],
        "linkedin_suggestions": [], "keyword_highlights": [],
    }


def _fallback_match() -> dict:
    return {
        "match_percentage": 0, "ats_score": 0,
        "missing_keywords": [], "missing_skills": [], "matched_keywords": [],
        "ats_pass_probability": "Unknown",
        "recommended_improvements": ["Please re-run the analysis."],
        "tailoring_tips": [], "role_fit_summary": "Analysis failed. Please try again.",
    }
