"""
AI Career Roadmap & Skill Gap Engine
Powered by Google Gemini API (REST v1beta with multi-model fallback)
"""

import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

# Models in order of priority (automatically falls back if 503/429/404 occurs)
GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]


def clean_json_response(raw_text: str) -> str:
    """Extract and sanitize JSON from model output, stripping markdown code fences."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")].strip()

    # If extra text precedes or follows JSON brackets, find outermost JSON object
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        return match.group(1)
    return cleaned


def call_gemini_api(
    prompt: str,
    api_key: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.2,
    response_json: bool = True,
    max_retries: int = 1,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Call Gemini REST API with automated multi-model fallback and fast timeouts.
    Returns: (response_text, model_used, error_message)
    """
    if not api_key or not api_key.strip():
        return None, None, "Missing Google Gemini API Key. Please provide a key in .env or the sidebar."

    api_key = api_key.strip()
    last_error = ""

    payload: Dict[str, Any] = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192,
        }
    }

    if response_json:
        payload["generationConfig"]["response_mime_type"] = "application/json"

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    for model_name in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=payload, timeout=45)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", ""), model_name, None
                    last_error = f"Model {model_name} returned empty candidates."
                elif resp.status_code in (429, 503):
                    last_error = f"Model {model_name} rate limit or high demand (HTTP {resp.status_code})."
                    time.sleep(0.5)
                    continue
                else:
                    last_error = f"Model {model_name} error (HTTP {resp.status_code}): {resp.text[:180]}"
                    break
            except requests.exceptions.RequestException as e:
                last_error = f"Network timeout with model {model_name}: {str(e)}"
                continue

    return None, None, f"All Gemini model fallbacks exhausted. Last error: {last_error}"


def generate_career_roadmap(
    current_skills: str,
    target_role: str,
    hours_per_week: int,
    career_level: str = "Student / Beginner",
    learning_style: str = "Practical & Project-Based",
    api_key: str = "",
) -> Dict[str, Any]:
    """
    Generate skills gap analysis, 8-week learning roadmap, and 3 portfolio projects.
    Returns structured dictionary.
    """
    total_hours = hours_per_week * 8

    system_instruction = (
        "You are an elite AI Career Coach, Principal Engineer, and Technical Hiring Manager. "
        "Your task is to analyze a student's current skills against their target job role, "
        "perform a rigorous skills gap analysis, create a realistic 8-week week-by-week learning roadmap "
        "calibrated exactly to their available study hours, and suggest 3 high-impact portfolio mini-projects."
    )

    prompt = f"""
Analyze the student's profile and generate the career transition plan:
- Target Job Role: {target_role}
- Current Skills: {current_skills}
- Available Study Time: {hours_per_week} hours/week (Total {total_hours} hours over 8 weeks)
- Experience Level: {career_level}
- Learning Style Preference: {learning_style}

Generate a comprehensive JSON object with these EXACT keys and structure:

{{
  "role_summary": {{
    "target_role": "{target_role}",
    "overview": "2-3 sentence overview of what this role entails and industry market demand in 2026.",
    "match_score": 45, // integer 0-100 indicating percentage match between current skills and target role
    "skills_possessed_count": 3, // count of relevant skills they already have
    "skills_to_learn_count": 6, // count of core skills they need to learn
    "total_recommended_hours": {total_hours},
    "readiness_verdict": "Encouraging, honest 2-sentence assessment of their feasibility to transition in 8 weeks."
  }},
  "skills_analysis": [
    // Include 8 to 12 skills total: both possessed skills AND missing skills
    {{
      "skill": "Skill Name",
      "status": "Have & Relevant", // Must be one of: "Have & Relevant", "Need to Learn", "Partial / Transferable"
      "category": "Programming / Data / Database / DevOps / Web / Core Concept",
      "priority": "High", // "High", "Medium", "Low"
      "current_level": "Beginner / Intermediate / None",
      "required_level": "Working Knowledge / Production Ready",
      "gap_notes": "How their current knowledge helps or what specific gap they must bridge."
    }}
  ],
  "roadmap_weeks": [
    // EXACTLY 8 ITEMS: week_number 1 through 8
    {{
      "week_number": 1,
      "phase": "Phase 1: Foundations & Prerequisites (Weeks 1-2)",
      "title": "Week Title",
      "weekly_hours": {hours_per_week},
      "objective": "Clear milestone goal for this week.",
      "key_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4"],
      "hands_on_milestone": "Concrete coding task or exercise to complete by Sunday.",
      "free_resources": [
        {{"title": "Resource Name", "type": "Documentation | Video Course | Practice Site", "link": "https://example.com or topic search"}}
      ]
    }}
  ],
  "portfolio_projects": [
    // EXACTLY 3 MINI PROJECTS: Beginner, Intermediate, Capstone
    {{
      "id": 1,
      "level": "Beginner / Foundation",
      "title": "Project Title",
      "description": "2-3 sentence description of the project problem, solution, and impact.",
      "skills_used": ["Skill A", "Skill B", "Skill C"],
      "tech_stack": ["Tool 1", "Tool 2"],
      "features": ["Feature 1", "Feature 2", "Feature 3"],
      "resume_bullet": "Strong action-verb bullet point for resume/LinkedIn (e.g. 'Engineered a... reducing... using...')."
    }},
    {{
      "id": 2,
      "level": "Intermediate / Applied",
      "title": "Project Title",
      "description": "...",
      "skills_used": ["..."],
      "tech_stack": ["..."],
      "features": ["..."],
      "resume_bullet": "..."
    }},
    {{
      "id": 3,
      "level": "Advanced / Capstone",
      "title": "Project Title",
      "description": "...",
      "skills_used": ["..."],
      "tech_stack": ["..."],
      "features": ["..."],
      "resume_bullet": "..."
    }}
  ],
  "interview_prep_tips": [
    "Actionable tip 1 on technical interviews or portfolio presentation.",
    "Actionable tip 2 on bridging past background during screening calls.",
    "Actionable tip 3 on GitHub repo presentation.",
    "Actionable tip 4 on behavioral / problem-solving discussions."
  ]
}}

Return ONLY valid JSON.
"""

    raw_text, model_used, error = call_gemini_api(
        prompt=prompt,
        api_key=api_key,
        system_instruction=system_instruction,
        temperature=0.25,
        response_json=True
    )

    if error or not raw_text:
        # If API fails or is unavailable, use high quality fallback template
        data = get_curated_fallback_roadmap(current_skills, target_role, hours_per_week)
        data["_generated_by"] = "Curated Offline Engine (API unavailable: " + (error or "No response") + ")"
        data["_is_offline"] = True
        return data

    try:
        cleaned = clean_json_response(raw_text)
        data = json.loads(cleaned)
        data["_generated_by"] = f"Google Gemini ({model_used})"
        data["_is_offline"] = False
        return data
    except Exception as e:
        # Fallback if JSON decode fails
        data = get_curated_fallback_roadmap(current_skills, target_role, hours_per_week)
        data["_generated_by"] = f"Curated Offline Engine (JSON parse fallback: {str(e)})"
        data["_is_offline"] = True
        return data


def ask_career_mentor(
    question: str,
    context: Dict[str, Any],
    api_key: str = "",
) -> str:
    """Answer student follow-up career questions grounded in their roadmap context."""
    role = context.get("role_summary", {}).get("target_role", "Target Role")
    skills = [s.get("skill") for s in context.get("skills_analysis", []) if s.get("status") == "Have & Relevant"]

    system_instruction = (
        "You are an encouraging, experienced Technical Mentor and Career Coach. "
        "Answer the student's question clearly, practically, and with concrete examples."
    )

    prompt = f"""
Student Target Role: {role}
Student Current Possessed Skills: {', '.join(skills) if skills else 'Beginner'}

Student Question:
{question}

Provide a helpful, structured, concise answer with bullet points and practical advice.
"""

    text, model, err = call_gemini_api(
        prompt=prompt,
        api_key=api_key,
        system_instruction=system_instruction,
        temperature=0.4,
        response_json=False
    )

    if err or not text:
        return f"Career Mentor Tip: For {role}, consistency is key. Break this topic into small daily coding sprints, document your progress on GitHub, and practice explaining your code aloud."

    return text.strip()


def get_curated_fallback_roadmap(current_skills: str, target_role: str, hours_per_week: int) -> Dict[str, Any]:
    """
    Curated high-quality fallback roadmap for offline demos, missing keys, or API outages.
    Ensures the student can ALWAYS demonstrate a working prototype without crashing.
    """
    total_hours = hours_per_week * 8
    target_role_lower = target_role.lower()

    is_data = any(w in target_role_lower for w in ["data", "ml", "machine learning", "ai", "deep learning"])
    is_web = any(w in target_role_lower for w in ["web", "full stack", "frontend", "backend", "react", "node"])

    if is_data:
        skills = [
            {"skill": "Python Basics", "status": "Have & Relevant", "category": "Programming", "priority": "High", "current_level": "Basic", "required_level": "Proficient", "gap_notes": "Strengthen functions, OOP, and data structures."},
            {"skill": "C Programming", "status": "Partial / Transferable", "category": "Core Concept", "priority": "Low", "current_level": "Intermediate", "required_level": "Not Required", "gap_notes": "Great for algorithmic thinking and memory concepts."},
            {"skill": "HTML / Basic Web", "status": "Partial / Transferable", "category": "Web", "priority": "Low", "current_level": "Basic", "required_level": "Basic", "gap_notes": "Helpful for web scraping and Streamlit UI styling."},
            {"skill": "Pandas & NumPy", "status": "Need to Learn", "category": "Data Science", "priority": "High", "current_level": "None", "required_level": "Production Ready", "gap_notes": "Essential for tabular data wrangling and numerical operations."},
            {"skill": "SQL & Relational Databases", "status": "Need to Learn", "category": "Database", "priority": "High", "current_level": "None", "required_level": "Intermediate", "gap_notes": "Must write complex queries, JOINs, aggregations, and window functions."},
            {"skill": "Data Visualization (Seaborn/Plotly)", "status": "Need to Learn", "category": "Analytics", "priority": "Medium", "current_level": "None", "required_level": "Working Knowledge", "gap_notes": "Create compelling charts to communicate insights to stakeholders."},
            {"skill": "Scikit-Learn Machine Learning", "status": "Need to Learn", "category": "Machine Learning", "priority": "High", "current_level": "None", "required_level": "Working Knowledge", "gap_notes": "Master regression, classification, cross-validation, and metrics."},
            {"skill": "Git & GitHub Version Control", "status": "Need to Learn", "category": "Dev Tools", "priority": "High", "current_level": "None", "required_level": "Working Knowledge", "gap_notes": "Crucial for showcasing portfolio code to hiring managers."}
        ]

        weeks = [
            {
                "week_number": 1,
                "phase": "Phase 1: Foundations & Data Wrangling (Weeks 1-2)",
                "title": "Python for Data Science & NumPy Vectors",
                "weekly_hours": hours_per_week,
                "objective": "Bridge basic Python to data manipulation with NumPy arrays.",
                "key_topics": ["List comprehensions & lambda functions", "NumPy arrays, slicing, indexing", "Array broadcasting & vectorized math", "Reading CSV and JSON files"],
                "hands_on_milestone": "Build a CLI statistics calculator that parses a raw CSV and outputs mean, median, std dev.",
                "free_resources": [{"title": "NumPy Quickstart Guide", "type": "Documentation", "link": "https://numpy.org/doc/stable/user/quickstart.html"}]
            },
            {
                "week_number": 2,
                "phase": "Phase 1: Foundations & Data Wrangling (Weeks 1-2)",
                "title": "Pandas DataFrames & Missing Data Mastery",
                "weekly_hours": hours_per_week,
                "objective": "Clean, filter, and transform real-world datasets with Pandas.",
                "key_topics": ["DataFrame indexing & Boolean filtering", "Handling null values & outliers", "GroupBy, aggregations & pivot tables", "Merging and joining datasets"],
                "hands_on_milestone": "Clean a messy real-world Kaggle dataset (e.g. Titanic or Housing) and export clean data.",
                "free_resources": [{"title": "Pandas 10-Minute Tutorial", "type": "Documentation", "link": "https://pandas.pydata.org/docs/user_guide/10min.html"}]
            },
            {
                "week_number": 3,
                "phase": "Phase 2: Exploratory Analysis & SQL (Weeks 3-4)",
                "title": "Exploratory Data Analysis (EDA) & Visualization",
                "weekly_hours": hours_per_week,
                "objective": "Uncover hidden patterns using Matplotlib, Seaborn, and Plotly.",
                "key_topics": ["Distribution plots, box plots & heatmaps", "Correlation matrices & feature relationships", "Interactive dashboards with Plotly", "Storytelling with business metrics"],
                "hands_on_milestone": "Create a 5-chart exploratory visual analysis notebook answering business questions.",
                "free_resources": [{"title": "Seaborn Tutorial Gallery", "type": "Tutorial", "link": "https://seaborn.pydata.org/tutorial.html"}]
            },
            {
                "week_number": 4,
                "phase": "Phase 2: Exploratory Analysis & SQL (Weeks 3-4)",
                "title": "SQL for Data Science & Database Querying",
                "weekly_hours": hours_per_week,
                "objective": "Query relational databases using SQLite and PostgreSQL.",
                "key_topics": ["SELECT, WHERE, GROUP BY, HAVING", "INNER, LEFT, RIGHT JOINs", "Window functions (RANK, OVER, ROW_NUMBER)", "Connecting Python to SQL databases via SQLAlchemy"],
                "hands_on_milestone": "Solve 15 LeetCode/HackerRank SQL practice problems and write a Python database extractor.",
                "free_resources": [{"title": "SQLBolt Interactive Lessons", "type": "Practice Site", "link": "https://sqlbolt.com"}]
            },
            {
                "week_number": 5,
                "phase": "Phase 3: Applied Machine Learning (Weeks 5-6)",
                "title": "Supervised Learning: Regression & Classification",
                "weekly_hours": hours_per_week,
                "objective": "Train and evaluate predictive models using Scikit-Learn.",
                "key_topics": ["Feature scaling & One-Hot Encoding", "Linear & Logistic Regression", "Decision Trees & Random Forests", "Train/Test split, K-Fold Cross Validation"],
                "hands_on_milestone": "Train a customer churn classifier with 80%+ accuracy and plot the confusion matrix.",
                "free_resources": [{"title": "Scikit-Learn User Guide", "type": "Documentation", "link": "https://scikit-learn.org/stable/user_guide.html"}]
            },
            {
                "week_number": 6,
                "phase": "Phase 3: Applied Machine Learning (Weeks 5-6)",
                "title": "Model Tuning, Evaluation Metrics & Unsupervised ML",
                "weekly_hours": hours_per_week,
                "objective": "Optimize models, prevent overfitting, and cluster data.",
                "key_topics": ["Precision, Recall, F1-Score & ROC-AUC curves", "Hyperparameter tuning (GridSearchCV, RandomizedSearchCV)", "K-Means clustering & PCA dimensionality reduction", "Feature importance interpretation"],
                "hands_on_milestone": "Perform hyperparameter optimization on your classifier and document accuracy improvements.",
                "free_resources": [{"title": "StatQuest ML Fundamentals", "type": "Video Course", "link": "https://www.youtube.com/@statquest"}]
            },
            {
                "week_number": 7,
                "phase": "Phase 4: Capstone & Portfolio Engineering (Weeks 7-8)",
                "title": "Model Deployment & Interactive Web Apps (Streamlit)",
                "weekly_hours": hours_per_week,
                "objective": "Turn trained models into live interactive web applications.",
                "key_topics": ["Serializing models with Joblib / Pickle", "Building Streamlit UI inputs and charts", "Deploying to Streamlit Cloud or Hugging Face Spaces", "Writing professional README.md with architecture diagram"],
                "hands_on_milestone": "Deploy your ML model with a public Streamlit web URL accessible by anyone.",
                "free_resources": [{"title": "Streamlit Documentation", "type": "Documentation", "link": "https://docs.streamlit.io"}]
            },
            {
                "week_number": 8,
                "phase": "Phase 4: Capstone & Portfolio Engineering (Weeks 7-8)",
                "title": "Portfolio Polishing, Resume Tailoring & Mock Interviews",
                "weekly_hours": hours_per_week,
                "objective": "Prepare GitHub repositories and practice answering technical interview questions.",
                "key_topics": ["GitHub repo READMEs, badges, and demo GIFs", "Translating code into resume impact bullets", "Core Data Science interview questions (bias-variance, p-values)", "Conducting self-recorded mock interview answers"],
                "hands_on_milestone": "Finalize 3 GitHub repos, pin them to your profile, and complete your updated resume.",
                "free_resources": [{"title": "GitHub Profile Readme Guide", "type": "Guide", "link": "https://docs.github.com/en/account-and-profile"}]
            }
        ]

        projects = [
            {
                "id": 1,
                "level": "Beginner / Foundation",
                "title": "Automated Exploratory Data Analysis & Cleaner App",
                "description": "An interactive web app where users upload any CSV and receive instant summary statistics, missing value reports, distribution charts, and cleaned CSV downloads.",
                "skills_used": ["Python", "Pandas", "Streamlit", "Plotly"],
                "tech_stack": ["Python 3.11+", "Pandas", "Streamlit", "Plotly Express"],
                "features": ["Drag-and-drop CSV uploader with auto type inference", "Outlier detection using IQR method", "Correlation heatmap with feature selector", "One-click cleaned CSV export button"],
                "resume_bullet": "Developed an interactive EDA dashboard in Streamlit & Pandas used to automate data cleaning and visualize distribution anomalies across 100k+ rows."
            },
            {
                "id": 2,
                "level": "Intermediate / Applied",
                "title": "Customer Churn Prediction & Risk Scorer",
                "description": "An end-to-end machine learning system that predicts subscription cancellation probability and provides personalized retention recommendations for at-risk accounts.",
                "skills_used": ["Scikit-Learn", "Feature Engineering", "Data Preprocessing", "Evaluation Metrics"],
                "tech_stack": ["Python", "Scikit-Learn", "XGBoost", "Streamlit"],
                "features": ["Preprocessed 20+ numerical & categorical features with standard scalers", "Trained Random Forest and XGBoost with 86% ROC-AUC score", "Interactive risk slider enabling managers to simulate retention discounts", "SHAP feature importance visualization explaining model predictions"],
                "resume_bullet": "Built an end-to-end churn prediction model achieving 86% ROC-AUC; created interactive Streamlit UI to simulate business intervention strategies."
            },
            {
                "id": 3,
                "level": "Advanced / Capstone",
                "title": "AI Financial Market Sentiment & Price Trend Analyzer",
                "description": "A production-grade analytics system combining web scraping, Gemini LLM sentiment classification of financial news, and predictive regression for market movement signals.",
                "skills_used": ["Gemini API", "API Integration", "Time Series / Regression", "Full Deployment"],
                "tech_stack": ["Python", "Google Gemini API", "Pandas", "Streamlit Cloud"],
                "features": ["Real-time financial headline fetching with caching", "Zero-shot sentiment tagging (Bullish/Bearish/Neutral) via Gemini API", "Interactive time-series chart overlaying sentiment scores on price trends", "Automated executive summary report generation in Markdown"],
                "resume_bullet": "Architected an AI financial intelligence app integrating Gemini API with live data streams to generate automated market sentiment analysis with sub-second latency."
            }
        ]
    else:
        # Default / General Software & Web / Tech Role
        skills = [
            {"skill": "C Programming", "status": "Have & Relevant", "category": "Core Concept", "priority": "Medium", "current_level": "Intermediate", "required_level": "Basic", "gap_notes": "Demonstrates strong understanding of memory, pointers, and algorithmic logic."},
            {"skill": "HTML / Basic Web", "status": "Have & Relevant", "category": "Frontend", "priority": "High", "current_level": "Basic", "required_level": "Proficient", "gap_notes": "Needs modern semantic HTML5, accessibility, and modern responsive layouts."},
            {"skill": "Python Basics", "status": "Have & Relevant", "category": "Backend", "priority": "High", "current_level": "Basic", "required_level": "Proficient", "gap_notes": "Solid basis; level up to REST APIs, web frameworks, and clean code."},
            {"skill": "CSS & Modern Styling", "status": "Need to Learn", "category": "Frontend", "priority": "High", "current_level": "None", "required_level": "Intermediate", "gap_notes": "Master Flexbox, CSS Grid, and responsive mobile-first design."},
            {"skill": "JavaScript (ES6+)", "status": "Need to Learn", "category": "Frontend", "priority": "High", "current_level": "None", "required_level": "Production Ready", "gap_notes": "Crucial for DOM manipulation, asynchronous fetch calls, and modern frameworks."},
            {"skill": "Backend Web Frameworks (FastAPI / Express)", "status": "Need to Learn", "category": "Backend", "priority": "High", "current_level": "None", "required_level": "Intermediate", "gap_notes": "Build RESTful endpoints, handle JSON payloads, and manage routing."},
            {"skill": "Database Design & SQL", "status": "Need to Learn", "category": "Database", "priority": "High", "current_level": "None", "required_level": "Intermediate", "gap_notes": "Design relational schemas, manage migrations, and write clean SQL queries."},
            {"skill": "Git & Deployment", "status": "Need to Learn", "category": "Dev Tools", "priority": "High", "current_level": "None", "required_level": "Working Knowledge", "gap_notes": "Version control with Git/GitHub and hosting applications on cloud platforms."}
        ]

        weeks = [
            {
                "week_number": 1,
                "phase": "Phase 1: Modern Web Foundations (Weeks 1-2)",
                "title": "Modern Semantic HTML5 & Responsive CSS",
                "weekly_hours": hours_per_week,
                "objective": "Build modern, accessible, and responsive layouts.",
                "key_topics": ["Semantic tags & accessibility", "Flexbox & CSS Grid layouts", "Mobile-first responsive media queries", "CSS variables & animations"],
                "hands_on_milestone": "Build a responsive personal developer portfolio landing page.",
                "free_resources": [{"title": "MDN Web Docs - HTML & CSS", "type": "Documentation", "link": "https://developer.mozilla.org"}]
            },
            {
                "week_number": 2,
                "phase": "Phase 1: Modern Web Foundations (Weeks 1-2)",
                "title": "Modern JavaScript (ES6+) Fundamentals",
                "weekly_hours": hours_per_week,
                "objective": "Master core JavaScript syntax, data structures, and DOM manipulation.",
                "key_topics": ["Let/const, arrow functions, destructuring", "DOM selectors and event listeners", "Array methods: map, filter, reduce", "Local storage and browser APIs"],
                "hands_on_milestone": "Build an interactive task tracker app with local storage persistence.",
                "free_resources": [{"title": "JavaScript.info Modern Tutorial", "type": "Tutorial", "link": "https://javascript.info"}]
            },
            {
                "week_number": 3,
                "phase": "Phase 2: Asynchronous JS & Backend APIs (Weeks 3-4)",
                "title": "Async JavaScript, Promises & Fetch API",
                "weekly_hours": hours_per_week,
                "objective": "Connect frontend interfaces to third-party REST APIs.",
                "key_topics": ["Async/Await and Promise error handling", "Calling public REST APIs with fetch()", "JSON serialization and parsing", "Loading states and UI error banners"],
                "hands_on_milestone": "Build a live Weather or Movie Search dashboard pulling data from a public API.",
                "free_resources": [{"title": "FreeCodeCamp JavaScript Algorithms", "type": "Course", "link": "https://www.freecodecamp.org"}]
            },
            {
                "week_number": 4,
                "phase": "Phase 2: Asynchronous JS & Backend APIs (Weeks 3-4)",
                "title": "Backend Development with Python FastAPI",
                "weekly_hours": hours_per_week,
                "objective": "Design, implement, and document production REST APIs.",
                "key_topics": ["Routing, path and query parameters", "Request/Response validation with Pydantic", "Automatic Swagger/OpenAPI documentation", "Handling CORS and HTTP status codes"],
                "hands_on_milestone": "Build a REST API backend with CRUD endpoints for a notes or bookmarking service.",
                "free_resources": [{"title": "FastAPI Official Tutorial", "type": "Documentation", "link": "https://fastapi.tiangolo.com/tutorial/"}]
            },
            {
                "week_number": 5,
                "phase": "Phase 3: Databases & Full-Stack Integration (Weeks 5-6)",
                "title": "Relational Databases & SQL with Python",
                "weekly_hours": hours_per_week,
                "objective": "Integrate SQLite/PostgreSQL with FastAPI using an ORM.",
                "key_topics": ["Relational table design & foreign keys", "SQLAlchemy ORM models & sessions", "Database migrations with Alembic", "Preventing SQL injection"],
                "hands_on_milestone": "Connect your CRUD API to a persistent SQLite database with relational tables.",
                "free_resources": [{"title": "SQLAlchemy Docs", "type": "Documentation", "link": "https://docs.sqlalchemy.org"}]
            },
            {
                "week_number": 6,
                "phase": "Phase 3: Databases & Full-Stack Integration (Weeks 5-6)",
                "title": "Authentication, Security & AI API Integration",
                "weekly_hours": hours_per_week,
                "objective": "Implement password hashing, JWT tokens, and integrate Gemini AI.",
                "key_topics": ["Password hashing with bcrypt", "JWT token generation and verification", "Calling Google Gemini API from backend endpoints", "API rate limiting and environment variable security"],
                "hands_on_milestone": "Add user signup/login and an AI summarizer feature to your web service.",
                "free_resources": [{"title": "Google AI Studio Quickstart", "type": "Documentation", "link": "https://ai.google.dev"}]
            },
            {
                "week_number": 7,
                "phase": "Phase 4: Capstone & Cloud Deployment (Weeks 7-8)",
                "title": "Full-Stack Deployment & Streamlit Showcase",
                "weekly_hours": hours_per_week,
                "objective": "Containerize or deploy the full application to free cloud hosting.",
                "key_topics": ["Building Streamlit frontend for rapid full-stack delivery", "Deploying on Streamlit Cloud or Render", "Managing environment variables and production secrets", "Writing automated health checks"],
                "hands_on_milestone": "Deploy your complete working prototype live on the web with a public URL.",
                "free_resources": [{"title": "Streamlit Cloud Deployment Guide", "type": "Guide", "link": "https://docs.streamlit.io/deploy/streamlit-community-cloud"}]
            },
            {
                "week_number": 8,
                "phase": "Phase 4: Capstone & Cloud Deployment (Weeks 7-8)",
                "title": "GitHub Portfolio Showcase & Technical Interview Prep",
                "weekly_hours": hours_per_week,
                "objective": "Finalize code repositories, craft resume bullets, and practice tech questions.",
                "key_topics": ["Writing comprehensive READMEs with diagrams and demo videos", "Clean Git commit history and branch management", "Explaining architecture decisions in technical interviews", "Mock coding problem solving"],
                "hands_on_milestone": "Publish 3 polished GitHub repositories with live demo links in your resume.",
                "free_resources": [{"title": "Tech Interview Handbook", "type": "Guide", "link": "https://www.techinterviewhandbook.org"}]
            }
        ]

        projects = [
            {
                "id": 1,
                "level": "Beginner / Foundation",
                "title": "Interactive Task & Habit Flow Application",
                "description": "A responsive productivity application featuring category filters, priority flags, progress statistics, and offline persistence using browser storage.",
                "skills_used": ["HTML5", "CSS3 / Flexbox", "JavaScript", "DOM Manipulation"],
                "tech_stack": ["HTML5", "CSS3", "Vanilla JavaScript ES6", "LocalStorage"],
                "features": ["Task creation with tags and due dates", "Completion progress percentage bar", "Filtered views (Active, Completed, Overdue)", "Local storage synchronization on reload"],
                "resume_bullet": "Developed a modular client-side productivity app using vanilla JavaScript and CSS Grid, implementing full state persistence with LocalStorage."
            },
            {
                "id": 2,
                "level": "Intermediate / Applied",
                "title": "Full-Stack AI Study Assistant & Quiz Generator",
                "description": "A complete web service where students paste lecture notes to automatically generate flashcards, practice quizzes, and concept explanations powered by Gemini.",
                "skills_used": ["Python", "FastAPI / Streamlit", "Gemini API", "JSON Schema"],
                "tech_stack": ["Python 3.11", "Streamlit", "Google Gemini API", "Pydantic"],
                "features": ["Document text extractor and concept chunker", "AI quiz generator returning multiple-choice questions with answer keys", "Interactive scoring and explanation mode", "Export quiz to printable Markdown or PDF"],
                "resume_bullet": "Engineered an AI study app integrating Gemini API to generate instant educational flashcards and adaptive quizzes, cutting study preparation time by 60%."
            },
            {
                "id": 3,
                "level": "Advanced / Capstone",
                "title": "Career Compass: AI Roadmap & Portfolio Architect",
                "description": "An end-to-end career intelligence web application comparing student profiles against tech roles to generate personalized 8-week roadmaps and project blueprints.",
                "skills_used": ["Streamlit", "Gemini API", "State Management", "Data Visualization"],
                "tech_stack": ["Python", "Streamlit", "Gemini Flash API", "Pandas", "CSS"],
                "features": ["Granular skill gap identification matrix", "8-week phased milestone planner with study hours calculation", "3-tier portfolio project architecture generator", "Interactive career mentor chat with live context grounding"],
                "resume_bullet": "Architected an interactive career roadmap platform powered by Gemini API, delivering personalized 8-week upskilling plans and portfolio architectures to aspiring developers."
            }
        ]

    return {
        "role_summary": {
            "target_role": target_role,
            "overview": f"The {target_role} role is in high demand across modern tech organizations. By leveraging your current background and executing a disciplined 8-week plan, you can build a competitive portfolio.",
            "match_score": 40,
            "skills_possessed_count": len([s for s in skills if "Have" in s["status"]]),
            "skills_to_learn_count": len([s for s in skills if "Need" in s["status"]]),
            "total_recommended_hours": total_hours,
            "readiness_verdict": f"You have strong transferable foundational skills. Allocating {hours_per_week} hours/week over 8 weeks ({total_hours} total hours) provides sufficient runway to bridge critical skill gaps and complete 3 portfolio projects."
        },
        "skills_analysis": skills,
        "roadmap_weeks": weeks,
        "portfolio_projects": projects,
        "interview_prep_tips": [
            f"Frame your previous skills ({current_skills}) as a unique cross-disciplinary advantage when interviewing for {target_role}.",
            "In technical interviews, walk interviewers through your GitHub project architectures, focusing on trade-offs and design decisions.",
            "Prepare 3 concise stories using the STAR method (Situation, Task, Action, Result) demonstrating how you learn new technologies rapidly.",
            "Pin your top 2 portfolio projects to your GitHub profile and ensure each has a live demo link and an eye-catching README."
        ]
    }
