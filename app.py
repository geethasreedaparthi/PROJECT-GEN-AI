"""
AI Career Roadmap & Skill Gap Finder
Web Application built with Streamlit and Google Gemini API.

Problem Statement:
Students know which job they want but don't know what to learn, in what order, to get there.

Inputs:
- Current skills (e.g. C, basic Python, HTML)
- Target job role (e.g. Data Scientist)
- Hours per week available to study

Outputs:
1. Skills already have vs skills to learn (as an interactive comparison table)
2. An 8-week week-by-week learning roadmap (calibrated to study hours)
3. 3 mini project ideas for the portfolio (Beginner, Intermediate, Capstone)
"""

import os
import json
from typing import Any, Dict, List
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from gemini_engine import (
    generate_career_roadmap,
    ask_career_mentor,
    get_curated_fallback_roadmap,
    GEMINI_MODELS,
)

# ---------------------------------------------------------------------------
# App Initialization & Environment
# ---------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="AI Career Roadmap & Skill Gap Finder",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for Modern, Professional Polish
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(240, 244, 255, 0.7), rgba(245, 247, 250, 0.9));
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid rgba(220, 226, 238, 0.8);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    
    /* Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }
    .hero-banner h1 {
        color: white;
        margin: 0 0 8px 0;
        font-size: 2.1rem;
        font-weight: 700;
    }
    .hero-banner p {
        color: rgba(255, 255, 255, 0.92);
        margin: 0;
        font-size: 1.05rem;
    }
    
    /* Project Cards */
    .project-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Badges */
    .badge-have {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-need {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-partial {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session State Setup
# ---------------------------------------------------------------------------
if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = None
if "current_skills_input" not in st.session_state:
    st.session_state.current_skills_input = "C, basic Python, HTML"
if "target_role_input" not in st.session_state:
    st.session_state.target_role_input = "Data Scientist"
if "hours_input" not in st.session_state:
    st.session_state.hours_input = 15
if "completed_weeks" not in st.session_state:
    st.session_state.completed_weeks = set()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------------------------
# Sidebar: Settings, Keys, and Actions
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=default_key,
        type="password",
        help="Free API key from Google AI Studio (aistudio.google.com). Loaded from .env if present.",
    )
    
    if api_key_input:
        st.success("API Key detected")
    else:
        st.info("No API key set. App will use Curated Offline Engine for instant testing.")
        st.caption("[Get a free key from Google AI Studio](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.subheader("📋 Assignment Spec")
    st.markdown(
        """
        **Problem Statement:**
        Students know which job they want but don't know what to learn, in what order.
        
        **Requirements:**
        - Compare current skills with target role
        - Skills table (Have vs Need to Learn)
        - 8-Week week-by-week roadmap
        - 3 Portfolio mini-projects
        - Built with Streamlit + Gemini API
        """
    )
    
    st.markdown("---")
    st.subheader("🛠️ Active Models")
    st.caption("Auto-fallback chain in order:")
    for i, m in enumerate(GEMINI_MODELS[:3], 1):
        st.code(f"{i}. {m}", language="text")

# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <h1>🎯 AI Career Roadmap & Skill Gap Finder</h1>
        <p>Bridge the gap between where you are and where you want to be. Compare your current skillset against your target job role, get a customized 8-week learning plan, and build 3 portfolio-worthy projects.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Quick Presets (One-click profile population)
# ---------------------------------------------------------------------------
st.markdown("##### ⚡ Quick Test Presets (Click to load sample profile)")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    if st.button("🎓 CS Student → Data Scientist", use_container_width=True):
        st.session_state.current_skills_input = "C, basic Python, HTML"
        st.session_state.target_role_input = "Data Scientist"
        st.session_state.hours_input = 15
        st.rerun()

with col_p2:
    if st.button("💻 Web Novice → Full Stack", use_container_width=True):
        st.session_state.current_skills_input = "HTML, basic CSS, basic JavaScript"
        st.session_state.target_role_input = "Full Stack Developer"
        st.session_state.hours_input = 18
        st.rerun()

with col_p3:
    if st.button("🤖 Python Hobbyist → ML Engineer", use_container_width=True):
        st.session_state.current_skills_input = "Python, Git, basic Linear Algebra"
        st.session_state.target_role_input = "Machine Learning Engineer"
        st.session_state.hours_input = 20
        st.rerun()

with col_p4:
    if st.button("📊 Non-Tech → Data Analyst", use_container_width=True):
        st.session_state.current_skills_input = "Excel, Basic SQL, Communication"
        st.session_state.target_role_input = "Data Analyst"
        st.session_state.hours_input = 12
        st.rerun()

st.markdown("---")

# ---------------------------------------------------------------------------
# Main Inputs Section
# ---------------------------------------------------------------------------
st.subheader("📝 Your Career Transition Profile")

col_left, col_right = st.columns(2)

POPULAR_ROLES = [
    "Data Scientist",
    "Full Stack Developer",
    "Machine Learning Engineer",
    "Data Analyst",
    "Backend Developer (Python/FastAPI)",
    "Frontend Developer (React)",
    "DevOps & Cloud Engineer",
    "AI/LLM Application Engineer",
    "Cybersecurity Analyst",
    "Custom (Type below)",
]

with col_left:
    role_choice = st.selectbox(
        "Target Job Role",
        options=POPULAR_ROLES,
        index=POPULAR_ROLES.index(st.session_state.target_role_input) if st.session_state.target_role_input in POPULAR_ROLES else len(POPULAR_ROLES)-1,
        help="Select a high-demand tech role or choose Custom to type your own.",
    )
    
    if role_choice == "Custom (Type below)":
        target_role = st.text_input("Enter your custom target role:", value=st.session_state.target_role_input)
    else:
        target_role = role_choice

    experience_level = st.selectbox(
        "Current Academic / Professional Level",
        options=["Student / Fresher", "Self-Taught / Junior", "Career Switcher from Non-Tech", "Mid-Level Engineer Upskilling"],
        index=0,
    )

with col_right:
    current_skills = st.text_area(
        "Current Skills (comma-separated or list)",
        value=st.session_state.current_skills_input,
        placeholder="e.g. C, basic Python, HTML, basic SQL",
        height=72,
        help="List programming languages, tools, frameworks, or concepts you have learned.",
    )
    
    hours_per_week = st.slider(
        "Hours Per Week Available to Study",
        min_value=5,
        max_value=40,
        value=st.session_state.hours_input,
        step=1,
        help="The 8-week curriculum depth and project timelines will be calibrated to this exact number.",
    )
    st.caption(f"⏱️ **Total study runway:** {hours_per_week * 8} hours over 8 weeks ({hours_per_week} hrs/week).")

# Action Button
col_btn, col_info = st.columns([1, 2])
with col_btn:
    generate_clicked = st.button("🚀 Generate Career Plan", type="primary", use_container_width=True)

if generate_clicked:
    if not current_skills.strip():
        st.error("Please enter at least one current skill (e.g. C, basic Python).")
    elif not target_role.strip():
        st.error("Please provide a target job role.")
    else:
        with st.spinner("Analyzing skill gaps, calibrating 8-week roadmap, and designing portfolio projects with Gemini AI..."):
            roadmap = generate_career_roadmap(
                current_skills=current_skills.strip(),
                target_role=target_role.strip(),
                hours_per_week=hours_per_week,
                career_level=experience_level,
                api_key=api_key_input,
            )
            st.session_state.roadmap_data = roadmap
            st.session_state.completed_weeks = set()
            st.session_state.current_skills_input = current_skills
            st.session_state.target_role_input = target_role
            st.session_state.hours_input = hours_per_week
            st.success("Roadmap generated successfully!")

# ---------------------------------------------------------------------------
# Results Display
# ---------------------------------------------------------------------------
data = st.session_state.roadmap_data

if data:
    st.markdown("---")
    
    summary = data.get("role_summary", {})
    match_score = summary.get("match_score", 40)
    skills_possessed = summary.get("skills_possessed_count", len([s for s in data.get("skills_analysis", []) if "Have" in s.get("status", "")]))
    skills_to_learn = summary.get("skills_to_learn_count", len([s for s in data.get("skills_analysis", []) if "Need" in s.get("status", "")]))
    total_hours = summary.get("total_recommended_hours", hours_per_week * 8)
    
    # Provider banner
    gen_by = data.get("_generated_by", "Google Gemini")
    st.caption(f"⚡ Plan generated using: **{gen_by}**")
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Skill Match Readiness", value=f"{match_score}%", delta=f"{100-match_score}% Gap to Bridge", delta_color="normal")
    with m2:
        st.metric(label="Skills You Already Have", value=skills_possessed, delta="Foundation", delta_color="off")
    with m3:
        st.metric(label="Key Skills to Learn", value=skills_to_learn, delta="Targeted", delta_color="inverse")
    with m4:
        st.metric(label="Total Study Runway", value=f"{total_hours} hrs", delta="8 Weeks", delta_color="off")
    
    # Readiness Verdict Box
    verdict = summary.get("readiness_verdict", "")
    overview = summary.get("overview", "")
    if verdict or overview:
        st.info(f"**AI Career Assessment:** {verdict} \n\n_{overview}_")

    # Interactive Progress Bar for 8-Week Tracker
    completed_count = len(st.session_state.completed_weeks)
    progress_val = completed_count / 8.0
    st.write(f"**Your 8-Week Execution Progress:** {completed_count}/8 Weeks Completed ({int(progress_val * 100)}%)")
    st.progress(progress_val)
    
    # Tabs for Outputs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 1. Skill Gap Analysis (Table)",
        "🗺️ 2. 8-Week Learning Roadmap",
        "🛠️ 3. Portfolio Mini Projects (3)",
        "💬 4. AI Career Mentor & Q&A",
        "📄 5. Export & Report",
    ])

    # -----------------------------------------------------------------------
    # TAB 1: SKILL GAP ANALYSIS (TABLE)
    # -----------------------------------------------------------------------
    with tab1:
        st.subheader("📊 Skills Already Have vs Skills to Learn")
        st.markdown(
            "This table compares your starting skillset with the market expectations for **{}**. "
            "Prioritize **High Priority** missing skills first.".format(summary.get("target_role", target_role))
        )
        
        skills_list = data.get("skills_analysis", [])
        if skills_list:
            filter_mode = st.radio(
                "Filter View:",
                ["All Skills", "Skills to Learn (Gap)", "Skills You Possess"],
                horizontal=True,
            )
            
            filtered = []
            for item in skills_list:
                status = item.get("status", "")
                if filter_mode == "Skills to Learn (Gap)" and "Need" not in status:
                    continue
                if filter_mode == "Skills You Possess" and ("Have" not in status and "Partial" not in status):
                    continue
                filtered.append({
                    "Skill": item.get("skill", ""),
                    "Status": item.get("status", ""),
                    "Category": item.get("category", ""),
                    "Priority": item.get("priority", "Medium"),
                    "Current Level": item.get("current_level", "Basic"),
                    "Required Level": item.get("required_level", "Working Knowledge"),
                    "Gap & Transition Notes": item.get("gap_notes", ""),
                })
            
            df = pd.DataFrame(filtered)
            
            # Format dataframe for display
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", help="Possessed vs Gap"),
                    "Priority": st.column_config.TextColumn("Priority", width="small"),
                    "Gap & Transition Notes": st.column_config.TextColumn("Gap & Action Plan", width="large"),
                }
            )
            
            # Category breakdown pills
            st.markdown("##### 🔍 Quick Summary")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**🟢 Skills You Have & Can Leverage:**")
                have_skills = [s["skill"] for s in skills_list if "Have" in s.get("status", "") or "Partial" in s.get("status", "")]
                if have_skills:
                    for s in have_skills:
                        st.markdown(f"- ✅ **{s}**")
                else:
                    st.write("No direct matches identified; you will build them in the roadmap.")
            with c2:
                st.markdown("**🔴 Skills You Need to Learn (Roadmap Focus):**")
                need_skills = [s["skill"] for s in skills_list if "Need" in s.get("status", "")]
                if need_skills:
                    for s in need_skills:
                        st.markdown(f"- 🎯 **{s}**")

    # -----------------------------------------------------------------------
    # TAB 2: 8-WEEK LEARNING ROADMAP
    # -----------------------------------------------------------------------
    with tab2:
        st.subheader("🗺️ 8-Week Week-by-Week Learning Roadmap")
        st.markdown(
            f"Curated for **{summary.get('target_role', target_role)}** calibrated to **{hours_per_week} hours/week**. "
            "Check off completed weeks to track your real progress!"
        )
        
        weeks = data.get("roadmap_weeks", [])
        
        for w in weeks:
            w_num = w.get("week_number", 1)
            w_title = w.get("title", f"Week {w_num}")
            w_phase = w.get("phase", "Learning Phase")
            w_hours = w.get("weekly_hours", hours_per_week)
            w_obj = w.get("objective", "")
            w_topics = w.get("key_topics", [])
            w_milestone = w.get("hands_on_milestone", "")
            w_resources = w.get("free_resources", [])
            
            is_done = w_num in st.session_state.completed_weeks
            
            with st.expander(f"{'✅' if is_done else '📌'} Week {w_num}: {w_title} ({w_hours} hrs)", expanded=(w_num == 1 or not is_done and w_num == len(st.session_state.completed_weeks) + 1)):
                col_w_left, col_w_right = st.columns([3, 1])
                
                with col_w_left:
                    st.markdown(f"**🏷️ Phase:** `{w_phase}`")
                    st.markdown(f"**🎯 Objective:** {w_obj}")
                    
                    st.markdown("**📚 Key Topics to Study:**")
                    for t in w_topics:
                        st.markdown(f"- {t}")
                    
                    st.markdown(f"**🔨 Hands-on Coding Milestone:**")
                    st.info(f"🏆 {w_milestone}")
                    
                    if w_resources:
                        st.markdown("**🌐 Free Curated Learning Resources:**")
                        for r in w_resources:
                            title = r.get("title", "Resource")
                            rtype = r.get("type", "Guide")
                            link = r.get("link", "#")
                            st.markdown(f"- [{title}]({link}) `({rtype})`")

                with col_w_right:
                    st.markdown("##### Progress Tracker")
                    chk = st.checkbox(f"Mark Week {w_num} Completed", value=is_done, key=f"week_chk_{w_num}")
                    if chk and w_num not in st.session_state.completed_weeks:
                        st.session_state.completed_weeks.add(w_num)
                        st.rerun()
                    elif not chk and w_num in st.session_state.completed_weeks:
                        st.session_state.completed_weeks.remove(w_num)
                        st.rerun()

    # -----------------------------------------------------------------------
    # TAB 3: 3 PORTFOLIO MINI PROJECTS
    # -----------------------------------------------------------------------
    with tab3:
        st.subheader("🛠️ 3 Portfolio Mini Projects to Prove Job Readiness")
        st.markdown(
            "Recruiters look for proof of skill. These three progressive projects bridge theory into real-world code "
            "that you can showcase on GitHub and your resume."
        )
        
        projects = data.get("portfolio_projects", [])
        
        for p in projects:
            p_id = p.get("id", 1)
            p_level = p.get("level", "Project")
            p_title = p.get("title", f"Portfolio Project {p_id}")
            p_desc = p.get("description", "")
            p_skills = p.get("skills_used", [])
            p_stack = p.get("tech_stack", [])
            p_features = p.get("features", [])
            p_bullet = p.get("resume_bullet", "")
            
            with st.container():
                st.markdown(
                    f"""
                    <div class="project-card">
                        <span class="badge-have" style="font-size:0.9rem;">Project {p_id}: {p_level}</span>
                        <h3 style="margin: 8px 0 10px 0;">{p_title}</h3>
                        <p style="color: #334155; font-size: 1.02rem;">{p_desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                col_p_left, col_p_right = st.columns([1, 1])
                with col_p_left:
                    st.markdown("**💻 Tech Stack & Skills Demonstrated:**")
                    all_tags = list(dict.fromkeys(p_stack + p_skills))
                    st.write(", ".join([f"`{t}`" for t in all_tags]))
                    
                    st.markdown("**📋 Key Features to Build:**")
                    for feat in p_features:
                        st.markdown(f"- ✅ {feat}")
                        
                with col_p_right:
                    st.markdown("**📄 Ready-to-Use Resume / LinkedIn Bullet Point:**")
                    st.code(p_bullet, language="text")
                    st.caption("💡 Copy and paste this directly onto your resume under your Projects section.")

                st.markdown("---")

    # -----------------------------------------------------------------------
    # TAB 4: AI CAREER MENTOR & INTERVIEW PREP
    # -----------------------------------------------------------------------
    with tab4:
        st.subheader("💬 AI Career Mentor & Interview Preparation")
        st.markdown("Ask any career transition question grounded in your 8-week plan and target role.")
        
        # Pre-made question chips
        st.markdown("##### 💡 Frequently Asked Questions (Click to Ask)")
        q_cols = st.columns(3)
        sample_q = ""
        with q_cols[0]:
            if st.button("❓ Top 5 Interview Questions for this role", use_container_width=True):
                sample_q = f"What are the top 5 technical interview questions for a {summary.get('target_role', target_role)} role and how should I answer them?"
        with q_cols[1]:
            if st.button("❓ How do I explain my past background?", use_container_width=True):
                sample_q = f"How should I explain my starting skills ({st.session_state.current_skills_input}) when interviewing for {summary.get('target_role', target_role)}?"
        with q_cols[2]:
            if st.button("❓ Which free certifications matter?", use_container_width=True):
                sample_q = f"What are the best free certifications or recognized badges for {summary.get('target_role', target_role)} to add to my LinkedIn?"

        # Display interview prep tips from data
        prep_tips = data.get("interview_prep_tips", [])
        if prep_tips:
            with st.expander("🎓 Career Coach Strategic Tips for Interviews", expanded=False):
                for tip in prep_tips:
                    st.markdown(f"- 💡 {tip}")
        
        user_question = st.text_input(
            "Ask your AI Career Mentor a question:",
            value=sample_q if sample_q else "",
            placeholder="e.g. How can I structure Project 2 to look professional on GitHub?",
        )
        
        if st.button("Send Question to Mentor", type="secondary"):
            if user_question.strip():
                with st.spinner("Career Mentor is analyzing your roadmap context..."):
                    mentor_answer = ask_career_mentor(
                        question=user_question,
                        context=data,
                        api_key=api_key_input,
                    )
                    st.session_state.chat_history.append((user_question, mentor_answer))
        
        if st.session_state.chat_history:
            st.markdown("##### Conversation History")
            for q, a in reversed(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.write(q)
                with st.chat_message("assistant"):
                    st.write(a)

    # -----------------------------------------------------------------------
    # TAB 5: EXPORT & REPORT
    # -----------------------------------------------------------------------
    with tab5:
        st.subheader("📄 Export Your Complete Career Roadmap")
        st.markdown("Download your customized 8-week plan and skill gap matrix for offline review or project submission.")
        
        # Build Markdown Export
        md_lines = [
            f"# AI Career Roadmap & Skill Gap Report: {summary.get('target_role', target_role)}",
            f"\n**Target Role:** {summary.get('target_role', target_role)}",
            f"**Current Skills:** {st.session_state.current_skills_input}",
            f"**Study Commitment:** {hours_per_week} hours/week ({total_hours} total hours over 8 weeks)",
            f"**Skill Match Score:** {match_score}%",
            f"\n## Executive Summary\n{summary.get('readiness_verdict', '')}\n\n{summary.get('overview', '')}\n",
            "\n## 1. Skill Gap Analysis Table\n",
            "| Skill | Status | Category | Priority | Gap Notes |",
            "|-------|--------|----------|----------|-----------|",
        ]
        
        for s in data.get("skills_analysis", []):
            md_lines.append(
                f"| {s.get('skill')} | {s.get('status')} | {s.get('category')} | {s.get('priority')} | {s.get('gap_notes')} |"
            )
            
        md_lines.append("\n## 2. 8-Week Week-by-Week Learning Roadmap\n")
        for w in data.get("roadmap_weeks", []):
            md_lines.append(f"### Week {w.get('week_number')}: {w.get('title')} ({w.get('weekly_hours')} hrs)")
            md_lines.append(f"- **Phase:** {w.get('phase')}")
            md_lines.append(f"- **Objective:** {w.get('objective')}")
            md_lines.append("- **Key Topics:**")
            for t in w.get("key_topics", []):
                md_lines.append(f"  - {t}")
            md_lines.append(f"- **Hands-on Milestone:** {w.get('hands_on_milestone')}")
            if w.get("free_resources"):
                md_lines.append("- **Free Resources:**")
                for r in w.get("free_resources", []):
                    md_lines.append(f"  - [{r.get('title')}]({r.get('link')}) ({r.get('type')})")
            md_lines.append("")
            
        md_lines.append("\n## 3. Portfolio Mini Projects\n")
        for p in data.get("portfolio_projects", []):
            md_lines.append(f"### Project {p.get('id')}: {p.get('title')} ({p.get('level')})")
            md_lines.append(f"{p.get('description')}\n")
            md_lines.append(f"- **Tech Stack:** {', '.join(p.get('tech_stack', []))}")
            md_lines.append("- **Key Features:**")
            for f in p.get("features", []):
                md_lines.append(f"  - {f}")
            md_lines.append(f"- **Resume Bullet:** `{p.get('resume_bullet')}`\n")
            
        markdown_content = "\n".join(md_lines)
        
        # Download buttons
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📥 Download Full Roadmap (Markdown .md)",
                data=markdown_content,
                file_name=f"career_roadmap_{summary.get('target_role', 'role').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_d2:
            # CSV of skills gap
            skills_df = pd.DataFrame(data.get("skills_analysis", []))
            csv_data = skills_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Skill Gap Table (CSV)",
                data=csv_data,
                file_name=f"skill_gap_analysis_{summary.get('target_role', 'role').lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("##### Preview of Generated Markdown Report")
        st.text_area("Markdown Preview", value=markdown_content, height=350)

else:
    # Empty State Guide
    st.info("👆 Adjust your profile above or select one of the **Quick Test Presets**, then click **Generate Career Plan** to get your personalized 8-week roadmap!")
