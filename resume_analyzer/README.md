# 📄 AI Resume Analyzer & ATS Scoring System

A production-ready, full-stack AI-powered Resume Analyzer built with **Streamlit**, **Google Gemini AI**, and **PyPDF2**. Fully responsive across Desktop, Laptop, Tablet, and Android mobile browsers.

---

## ✨ Features

### Core
- 📤 **PDF Resume Upload** — drag-and-drop, file validation, up to 10 MB
- 🔍 **Text Extraction** — multi-page PDF parsing via PyPDF2
- 🤖 **AI Analysis** — Google Gemini powers all insights
- 📊 **Resume Score (0–100)** — overall quality assessment
- 🛡 **ATS Score (0–100)** — applicant tracking system compatibility
- 🛠 **Skills Identification** — technical and soft skills
- ❌ **Missing Skills** — gaps vs industry expectations
- 💼 **Experience, Education & Projects Summary**
- 💡 **Improvement Suggestions** — actionable resume edits
- 🚀 **Career Recommendations**

### Job Match (Optional)
- 🎯 **Job Description Matching** — paste any job posting
- 📈 **Match Percentage** — keyword & skill overlap score
- 🔑 **Missing Keywords** — add these to your resume
- 🏆 **ATS Pass Probability** — Low / Medium / High
- ✏️ **Tailoring Tips** — how to customize your resume

### Dashboard
- 📉 **Gauge Charts** — visual score rings
- 🕸 **Radar Chart** — multi-dimension skill view
- 🏷 **Color-coded Tags** — skills, keywords, gaps
- 📥 **PDF Report Download** — full branded report via ReportLab

### Bonus
- ✨ AI-generated Professional Summary
- 🎤 Interview Preparation Tips
- 🔗 LinkedIn Profile Suggestions
- 🔑 Keyword Highlight Panel

---

## 📁 Project Structure

```
resume_analyzer/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .streamlit/
│   └── config.toml          # Streamlit theme & server config
├── utils/
│   ├── __init__.py
│   ├── parser.py            # PDF text extraction (PyPDF2)
│   ├── analyzer.py          # Gemini AI analysis & job matching
│   └── report_generator.py  # PDF report creation (ReportLab)
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & navigate
```bash
git clone https://github.com/yourname/resume-analyzer.git
cd resume_analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key

**Option A — .env file (recommended)**
```bash
cp .env.example .env
# Edit .env and paste your key:
# GEMINI_API_KEY=AIza...
```

**Option B — sidebar input**
Enter your key directly in the app's sidebar at runtime.

Get a free Gemini API key at: https://aistudio.google.com

### 5. Run the app
```bash
streamlit run app.py
```

Visit http://localhost:8501 in your browser.

---

## 🌐 Deployment

### Streamlit Community Cloud (Free)

1. Push this repo to GitHub
2. Visit https://share.streamlit.io
3. Connect your GitHub repo
4. Set `app.py` as the entry point
5. Add `GEMINI_API_KEY` under **Settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "AIza..."
   ```
6. Deploy — you'll get a public URL

### Railway / Render

```bash
# Procfile
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Set `GEMINI_API_KEY` in environment variables on the platform dashboard.

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t resume-analyzer .
docker run -p 8501:8501 -e GEMINI_API_KEY=AIza... resume-analyzer
```

---

## 📱 Responsive Design

| Device | Viewport | Status |
|--------|----------|--------|
| Android Mobile | ~375px | ✅ |
| Tablet | ~768px | ✅ |
| Laptop | ~1024px | ✅ |
| Desktop | 1440px+ | ✅ |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + custom CSS |
| AI | Google Gemini 1.5 Flash |
| PDF Parsing | PyPDF2 |
| Charts | Plotly |
| PDF Reports | ReportLab |
| Env Config | python-dotenv |

---

## 📝 License

MIT — free to use and modify.
