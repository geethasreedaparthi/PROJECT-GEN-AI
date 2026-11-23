---
title: AI Career Roadmap & Skill Gap Finder
emoji: 🎯
colorFrom: blue
colorTo: cyan
sdk: streamlit
app_file: app.py
python_version: "3.12"
short_description: Compare current skills with a target job and generate an 8-week learning plan and portfolio projects.
tags:
  - career
  - education
  - generative-ai
  - roadmap
---

# 🎯 AI Career Roadmap & Skill Gap Finder

An interactive web prototype built with **Streamlit** and **Google Gemini API** that helps students transition into their dream tech jobs by identifying skill gaps, generating a personalized 8-week learning curriculum, and designing 3 portfolio-worthy projects.

---

## 📌 Problem Statement

> **Problem:** Students know which job they want but don’t know what to learn, in what order, to get there.  
> **Build:** An app that compares the student’s current skills with a target job and creates a learning plan.  
> **Input:** Current skills (e.g. C, basic Python, HTML); target job role (e.g. Data Scientist); hours per week available to study.  
> **Output:**
> 1. **Skills already have vs skills to learn** (as a structured comparison table)
> 2. **An 8-week week-by-week learning roadmap** (calibrated to weekly study hours)
> 3. **3 mini project ideas for the portfolio** (Beginner, Intermediate, Capstone with resume bullets)  
> **Tools:** Python + Streamlit + Google Gemini API

---

## 🚀 Key Features

- **⚡ 1-Click Profile Presets:** Instantly test with sample profiles:
  - *CS Student → Data Scientist* (`C, basic Python, HTML`)
  - *Web Novice → Full Stack Developer* (`HTML, CSS, JavaScript`)
  - *Python Hobbyist → Machine Learning Engineer* (`Python, Git, Linear Algebra`)
  - *Non-Tech Switcher → Data Analyst* (`Excel, SQL, Communication`)
- **📊 Granular Skill Gap Analysis:**
  - Clear table separating *Skills Possessed* vs *Skills to Learn*.
  - Categorization (Programming, Databases, ML, Tools), priority flags (High/Medium/Low), and actionable transition notes.
  - Overall **Skill Match Readiness Score (%)**.
- **🗺️ Phased 8-Week Learning Roadmap:**
  - Divided into 4 progressive phases (Foundations, Core Concepts, Advanced, Capstone).
  - Day-by-day and topic-by-topic breakdowns calibrated to the student's exact weekly study hours.
  - Concrete hands-on coding milestones for every week.
  - Curated free learning resources with links (MDN, Pandas, Scikit-Learn, SQLBolt, etc.).
  - **Interactive Progress Tracker** with checkboxes that update real-time completion progress!
- **🛠️ 3 Portfolio Mini Projects:**
  - **Project 1 (Beginner):** Solidifies foundational concepts.
  - **Project 2 (Intermediate):** Integrates multiple new skills into a working tool.
  - **Project 3 (Capstone):** Production-grade full-stack / AI app to impress hiring managers.
  - Each project includes a **copy-ready resume bullet point** formatted with action verbs and impact metrics.
- **💬 Interactive AI Career Mentor:**
  - In-app chatbot grounded in the student's roadmap to ask interview questions, technical advice, or GitHub structuring tips.
- **📄 One-Click Export:**
  - Export complete plan as formatted Markdown (`.md`).
  - Export Skill Gap Analysis as CSV (`.csv`).
- **🛡️ Rock-Solid Resilience:**
  - Primary model: Google Gemini (`gemini-3.6-flash`).
  - Automated fallback chain across Gemini models to handle temporary demand spikes.
  - Built-in Curated Offline Engine ensures the prototype **never crashes**, even without internet or an API key!

---

## 💻 Tech Stack

| Component | Tool / Library | Purpose |
|---|---|---|
| **Language** | Python 3.10+ / 3.12 | Core development language |
| **Web Framework** | Streamlit | Fast, modern interactive web interface |
| **Generative AI** | Google Gemini API (v1beta) | Structured reasoning, gap analysis, curriculum design |
| **Data Handling** | Pandas | Skill matrix manipulation & CSV export |
| **Networking** | Requests | Direct REST API calls to Google Gemini |
| **Environment** | python-dotenv | Secure API key management |

---

## 🛠️ Installation & Local Setup

### 1. Clone or Open the Repository
```bash
cd "c:\Users\GEETHASRI\OneDrive\Desktop\GEN AI TASK 2"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API Key
Create or edit `.env` in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey). If left blank, the app runs in Curated Offline Engine mode for instant evaluation.)*

### 4. Run the Application
```bash
python -m streamlit run app.py
```
Open your browser at **[http://localhost:8501](http://localhost:8501)**.

---

## 🧠 Code Architecture & How to Explain It (Viva / Presentation)

When explaining this prototype to an evaluator or interviewer:

### 1. `gemini_engine.py` (AI Backend)
- **`call_gemini_api()`**: Sends an HTTP POST request to Google's REST endpoint (`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`).
- **Prompt Engineering**: Uses system instructions to position the AI as a Principal Engineer and Hiring Manager. We specify a strict JSON schema (`response_mime_type: application/json`) to guarantee deterministic keys for the skills table, 8-week curriculum, and 3 projects.
- **Multi-Model Fallback**: If a model returns HTTP 503 (high demand) or 429 (rate limit), the engine automatically tries the next model (`gemini-3.6-flash` → `gemini-3.5-flash-lite` → `gemini-flash-lite-latest`).
- **Curated Offline Fallback**: If all network attempts fail or no key is present, the app serves pre-computed, high-fidelity curriculum data so the demo runs seamlessly.

### 2. `app.py` (Interactive Frontend)
- **State Management**: Uses `st.session_state` to store user inputs, generated roadmap data, checkbox completion states, and career chat history across re-renders.
- **Dynamic Pacing Calculation**: Total study runway is dynamically calculated as `Hours/Week * 8 Weeks`.
- **Progress Tracking**: Checking off weekly milestones dynamically updates the progress bar (`completed_count / 8.0`).
- **Exporting**: Generates downloadable Markdown files and CSV tables directly in memory using `st.download_button`.

---

## ☁️ Free Cloud Deployment (Bonus)

### Deploy to Streamlit Community Cloud (Recommended - Free)
1. Push this folder to a GitHub repository.
2. Sign in to [share.streamlit.io](https://share.streamlit.io) using GitHub.
3. Click **"New app"**, select your repo, branch (`main`), and file path (`app.py`).
4. In **Advanced settings → Secrets**, add your key:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   ```
5. Click **Deploy**. Your app will be live at `https://<your-app-name>.streamlit.app`!

### Deploy to Hugging Face Spaces (Alternative - Free)
1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) and choose **Streamlit**.
2. Push `app.py`, `gemini_engine.py`, `requirements.txt`, and `README.md`.
3. In **Settings → Variables and Secrets**, add `GEMINI_API_KEY`.
4. Hugging Face builds and hosts the app automatically.

---

## 📄 License
MIT License. Built for Gen AI Individual Prototype Assignment.
