"""
Main Streamlit application for Resume Analyzer and Builder
Enhanced with Gemini AI integration for smart suggestions
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import tempfile
from datetime import datetime
import re
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from parser import ResumeParser
from analyzer import ResumeAnalyzer
from skills import JOB_ROLES_SKILLS, get_all_job_roles, get_skills_for_role, get_keywords_for_role
from generator import ResumeBuilder, format_resume_data
from llm_integration import LLMResumeAssistant

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer & Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .score-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
    .danger-text {
        color: #dc3545;
        font-weight: bold;
    }
    .critical-skill {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .section-score {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .suggestion-box {
        background-color: #e3f2fd;
        padding: 10px;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
        border-radius: 5px;
    }
    .ai-suggestion {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 15px;
        border-left: 4px solid #764ba2;
        margin: 10px 0;
        border-radius: 5px;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 3px solid #4CAF50;
    }
    .stTextArea textarea {
        font-family: monospace;
    }
    .api-status {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .api-active {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .api-inactive {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_analyzer():
    return ResumeAnalyzer()

@st.cache_resource
def init_builder():
    return ResumeBuilder()

@st.cache_resource
def init_llm():
    return LLMResumeAssistant()

analyzer = init_analyzer()
builder = init_builder()
llm_assistant = init_llm()
parser = ResumeParser()

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_section' not in st.session_state:
    st.session_state.current_section = "analysis"

# Sidebar navigation
st.sidebar.title("📄 Navigation")
page = st.sidebar.radio(
    "Choose an option",
    ["📊 Resume Analyzer", "🤖 AI Resume Assistant", "📝 Resume Builder"]
)

# Gemini Configuration in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Gemini AI Settings")

# Check if API key is already configured
api_key_configured = llm_assistant.has_valid_key()

if api_key_configured:
    key_source_label = ".env file" if llm_assistant.key_source == "env" else "sidebar input"
    st.sidebar.markdown("""
    <div class="api-status api-active">
    ✅ <b>Gemini API Active</b><br>
    Using model: <b>Gemini 2.5 Flash</b>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption(f"Loaded from: {key_source_label}")
    
    if llm_assistant.key_source == "manual" and st.sidebar.button("🗑️ Clear Session Key", use_container_width=True):
        llm_assistant.clear_api_key()
        st.session_state.chat_history = []
        st.rerun()
    elif llm_assistant.key_source == "env":
        st.sidebar.info("Gemini key is being loaded from `.env`. Edit `.env` if you want to change or remove it.")
else:
    st.sidebar.markdown("""
    <div class="api-status api-inactive">
    ⚠️ <b>Gemini API Key Required</b><br>
    No Gemini key found in `.env` or the current session
    </div>
    """, unsafe_allow_html=True)
    existing_key_message = llm_assistant.get_key_status_message()
    if "placeholder" in existing_key_message.lower():
        st.sidebar.warning(existing_key_message)
    
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter your API key (starts with AIza...)",
        help="Get your free API key from Google AI Studio"
    )
    
    if api_key:
        with st.spinner("Configuring Gemini API..."):
            llm_assistant.set_api_key(api_key)
            st.sidebar.success("✅ API Key configured for this session")
            st.rerun()
    
    st.sidebar.markdown("""
    ---
    **📌 How to get your FREE Gemini API Key:**
    
    1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Sign in with your Google account
    3. Click "Create API Key"
    4. Copy your key (starts with AIza...)
    5. Paste it above
    
    ✅ Free tier includes:
    - 60 requests per minute
    - Gemini 2.5 Flash model
    - No credit card required
    """)

# Display API status in main area if not configured
if not api_key_configured and page != "📝 Resume Builder":
    st.info("""
    🤖 **Enable AI Features**: Add your Gemini API key in the sidebar to get AI-powered resume suggestions and chat assistance.
    
    *Don't have a key? Get one for free from [Google AI Studio](https://makersuite.google.com/app/apikey)*
    """)

def extract_resume_text(uploaded_file):
    """Extract text from uploaded resume"""
    if uploaded_file is not None:
        try:
            text = parser.extract_text(uploaded_file)
            if text:
                return text
            else:
                st.error("Could not extract text from file. Please check the file format.")
                return None
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None
    return None

def calculate_section_scores(resume_text: str, skills: set, required_skills: list) -> dict:
    """Calculate individual section scores"""
    text_lower = resume_text.lower()
    
    # Skills score (based on match percentage)
    required_set = set(skill.lower() for skill in required_skills)
    matched_skills = skills.intersection(required_set)
    skills_score = (len(matched_skills) / len(required_set) * 100) if required_set else 0
    
    # Projects score (check for project section and quality)
    projects_score = 0
    if 'project' in text_lower:
        projects_score += 30
        if any(tech in text_lower for tech in ['python', 'java', 'javascript', 'react', 'sql']):
            projects_score += 20
        if re.search(r'developed|built|created|implemented', text_lower):
            projects_score += 30
        if re.search(r'github\.com|gitlab\.com|bitbucket', text_lower):
            projects_score += 20
    
    # Experience score
    experience_score = 0
    if 'experience' in text_lower or 'work' in text_lower:
        experience_score += 30
        if re.search(r'\d+%|\$\d+|\d+\s*(?:years|months|projects)', text_lower):
            experience_score += 30
        strong_verbs = ['developed', 'led', 'managed', 'created', 'implemented', 'designed']
        if any(verb in text_lower for verb in strong_verbs):
            experience_score += 20
        if re.search(r'\d{4}\s*-\s*\d{4}|present|current', text_lower):
            experience_score += 20
    
    # Education score
    education_score = 0
    if 'education' in text_lower or 'degree' in text_lower or 'university' in text_lower:
        education_score += 40
        if 'gpa' in text_lower or 'cgpa' in text_lower:
            education_score += 30
        if re.search(r'bachelor|master|phd|b\.tech|m\.tech', text_lower, re.IGNORECASE):
            education_score += 30
    
    return {
        'skills': round(skills_score, 1),
        'projects': round(projects_score, 1),
        'experience': round(experience_score, 1),
        'education': round(education_score, 1)
    }

def determine_resume_level(scores: dict, ats_score: float) -> tuple:
    """Determine resume level based on scores"""
    avg_score = (scores['skills'] + scores['projects'] + scores['experience'] + scores['education']) / 4
    
    if ats_score >= 80 or avg_score >= 80:
        return "Expert", "🌟", "#28a745"
    elif ats_score >= 60 or avg_score >= 60:
        return "Intermediate", "📈", "#ffc107"
    else:
        return "Beginner", "📚", "#dc3545"

def calculate_selection_chance(ats_score: float, section_scores: dict) -> float:
    """Calculate selection chance percentage"""
    weight_ats = 0.5
    weight_sections = 0.5
    
    avg_section = sum(section_scores.values()) / len(section_scores)
    selection_chance = (ats_score * weight_ats) + (avg_section * weight_sections)
    
    return min(round(selection_chance, 1), 95)

def get_critical_missing_skills(missing_skills: list, resume_text: str) -> list:
    """Identify critical missing skills"""
    critical = []
    high_demand_skills = ['python', 'java', 'sql', 'javascript', 'react', 'aws', 'docker', 
                         'git', 'machine learning', 'deep learning', 'tensorflow', 'pytorch']
    
    for skill in missing_skills:
        skill_lower = skill.lower()
        if any(critical_skill in skill_lower for critical_skill in high_demand_skills):
            critical.append(skill)
    
    return critical[:3]

def generate_enhanced_suggestions(section_scores: dict, missing_skills: list, 
                                 resume_text: str, matched_skills: list) -> list:
    """Generate enhanced suggestions with priority"""
    suggestions = []
    text_lower = resume_text.lower()
    
    critical_missing = get_critical_missing_skills(missing_skills, resume_text)
    for skill in critical_missing[:2]:
        suggestions.append(f"🚨 Add **{skill}** (Critical for this role)")
    
    if section_scores['skills'] < 70:
        if missing_skills:
            suggestions.append(f"📚 Add {len(missing_skills[:3])} missing skills: {', '.join(missing_skills[:3])}")
    
    if section_scores['projects'] < 60:
        suggestions.append("💼 Add **real-world projects** showcasing your technical skills")
        if section_scores['projects'] < 40:
            suggestions.append("📝 Include **GitHub links** and **live demos** for your projects")
    
    if section_scores['experience'] < 60:
        suggestions.append("⚡ Use **stronger action verbs** (Developed, Architected, Optimized, Led)")
        if not re.search(r'\d+%|\$\d+', text_lower):
            suggestions.append("📊 Add **quantifiable achievements** (e.g., 'Increased performance by 40%')")
    
    weak_verbs = ['worked on', 'did', 'handled', 'responsible for', 'assisted']
    found_weak = [verb for verb in weak_verbs if verb in text_lower]
    if found_weak:
        suggestions.append(f"💪 Replace weak verbs like '{found_weak[0]}' with stronger alternatives")
    
    if 'summary' not in text_lower and 'profile' not in text_lower:
        suggestions.append("📋 Add a **professional summary** at the top of your resume")
    
    return suggestions[:6]

def display_enhanced_results(ats_score: float, section_scores: dict, 
                            matched_skills: list, missing_skills: list, 
                            resume_text: str, job_role: str):
    """Display enhanced results with better formatting"""
    
    selection_chance = calculate_selection_chance(ats_score, section_scores)
    resume_level, level_icon, level_color = determine_resume_level(section_scores, ats_score)
    critical_missing = get_critical_missing_skills(missing_skills, resume_text)
    
    # Main ATS Score Card
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="font-size: 48px; margin: 0;">{ats_score}%</h2>
            <p style="margin: 0;">ATS Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h2 style="font-size: 48px; margin: 0;">{selection_chance}%</h2>
            <p style="margin: 0;">Selection Chance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h2 style="font-size: 32px; margin: 0;">{level_icon} {resume_level}</h2>
            <p style="margin: 0;">Resume Level</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section Scores with progress bars
    st.subheader("📊 Section Scores")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="section-score">
            <b>🎯 Skills</b><br>
            <progress value="{section_scores['skills']}" max="100" style="width: 100%; height: 20px; border-radius: 10px;"></progress>
            <b style="float: right;">{section_scores['skills']}%</b>
        </div>
        <br>
        <div class="section-score">
            <b>💼 Projects</b><br>
            <progress value="{section_scores['projects']}" max="100" style="width: 100%; height: 20px; border-radius: 10px;"></progress>
            <b style="float: right;">{section_scores['projects']}%</b>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="section-score">
            <b>⚡ Experience</b><br>
            <progress value="{section_scores['experience']}" max="100" style="width: 100%; height: 20px; border-radius: 10px;"></progress>
            <b style="float: right;">{section_scores['experience']}%</b>
        </div>
        <br>
        <div class="section-score">
            <b>🎓 Education</b><br>
            <progress value="{section_scores['education']}" max="100" style="width: 100%; height: 20px; border-radius: 10px;"></progress>
            <b style="float: right;">{section_scores['education']}%</b>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Skills Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Skills")
        if matched_skills:
            for skill in matched_skills[:10]:
                st.markdown(f"✓ {skill}")
            if len(matched_skills) > 10:
                st.markdown(f"... and {len(matched_skills) - 10} more")
        else:
            st.markdown("No matching skills found")
    
    with col2:
        st.subheader("❌ Missing Skills")
        if missing_skills:
            for skill in missing_skills[:10]:
                if skill in critical_missing:
                    st.markdown(f"<span class='critical-skill'>⚠️ {skill} (Critical)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"✗ {skill}")
            if len(missing_skills) > 10:
                st.markdown(f"... and {len(missing_skills) - 10} more")
        else:
            st.markdown("No missing skills! Great match!")
    
    st.markdown("---")
    
    # Suggestions
    st.subheader("📌 Suggestions for Improvement")
    suggestions = generate_enhanced_suggestions(section_scores, missing_skills, resume_text, matched_skills)
    
    for i, suggestion in enumerate(suggestions, 1):
        st.markdown(f"""
        <div class="suggestion-box">
            {suggestion}
        </div>
        """, unsafe_allow_html=True)
    
    # Radar Chart for visual representation
    st.subheader("📈 Skills Radar Analysis")
    
    categories = ['Skills Match', 'Projects', 'Experience', 'Education', 'Format', 'Keywords']
    values = [
        section_scores['skills'],
        section_scores['projects'],
        section_scores['experience'],
        section_scores['education'],
        ats_score * 0.8,
        ats_score * 0.9
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color='rgba(102, 126, 234, 0.8)'),
        line=dict(color='rgba(102, 126, 234, 1)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Improvement tips based on scores
    st.markdown("---")
    st.subheader("🎯 Quick Improvement Tips")
    
    tips_col1, tips_col2, tips_col3 = st.columns(3)
    
    with tips_col1:
        if section_scores['skills'] < 70:
            st.info("💡 **Skills Gap**\n\nAdd missing technical skills through online courses or personal projects")
        else:
            st.success("✅ Strong skills section!")
    
    with tips_col2:
        if section_scores['projects'] < 60:
            st.info("💡 **Project Portfolio**\n\nBuild 2-3 strong projects and host them on GitHub")
        else:
            st.success("✅ Good project portfolio!")
    
    with tips_col3:
        if section_scores['experience'] < 60:
            st.info("💡 **Experience Enhancement**\n\nUse STAR method (Situation, Task, Action, Result) for achievements")
        else:
            st.success("✅ Well-documented experience!")

# Main content
if page == "📊 Resume Analyzer":
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume and get detailed analysis with improvement suggestions")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )
    
    with col2:
        analysis_type = st.radio(
            "Analysis Type",
            ["Job Role", "Job Description"],
            horizontal=True
        )
    
    job_role = None
    job_description = None
    
    if analysis_type == "Job Role":
        job_role = st.selectbox(
            "Select Job Role",
            get_all_job_roles(),
            help="Choose the job role you're applying for"
        )
    else:
        job_description = st.text_area(
            "Paste Job Description",
            height=150,
            placeholder="Paste the complete job description here...",
            help="The system will compare your resume with this job description"
        )
    
    if st.button("🔍 Analyze Resume", use_container_width=True):
        if uploaded_file is None:
            st.error("Please upload a resume file first")
        elif analysis_type == "Job Role" and not job_role:
            st.error("Please select a job role")
        elif analysis_type == "Job Description" and not job_description:
            st.error("Please enter a job description")
        else:
            with st.spinner("Analyzing your resume..."):
                resume_text = extract_resume_text(uploaded_file)
                
                if resume_text:
                    st.session_state.resume_text = resume_text
                    
                    if analysis_type == "Job Role":
                        required_skills = get_skills_for_role(job_role)
                        keywords = get_keywords_for_role(job_role)
                    else:
                        required_skills = []
                        keywords = []
                    
                    resume_skills = analyzer.extract_skills(resume_text)
                    skill_match = analyzer.calculate_skill_match(resume_skills, required_skills)
                    
                    if analysis_type == "Job Role":
                        keyword_score = analyzer.calculate_keyword_relevance(resume_text, keywords=keywords)
                    else:
                        keyword_score = analyzer.calculate_keyword_relevance(resume_text, job_description=job_description)
                    
                    structure_score = analyzer.check_resume_structure(resume_text)
                    grammar_score = analyzer.check_grammar(resume_text)
                    
                    ats_results = analyzer.calculate_ats_score(
                        skill_match, keyword_score, structure_score, grammar_score
                    )
                    
                    section_scores = calculate_section_scores(resume_text, resume_skills, required_skills)
                    
                    st.session_state.analysis_results = {
                        'ats_score': ats_results['total_score'],
                        'section_scores': section_scores,
                        'matched_skills': skill_match['matched_skills'],
                        'missing_skills': skill_match['missing_skills'],
                        'resume_text': resume_text,
                        'job_role': job_role if job_role else "Job Description Match",
                        'required_skills': required_skills
                    }
                    st.session_state.analysis_done = True
                    
                    display_enhanced_results(
                        ats_results['total_score'],
                        section_scores,
                        skill_match['matched_skills'],
                        skill_match['missing_skills'],
                        resume_text,
                        job_role if job_role else "Job Description Match"
                    )
                    
                    # Generate AI Suggestions if API key is configured
                    if llm_assistant.has_valid_key():
                        st.markdown("---")
                        st.subheader("🤖 Gemini AI-Powered Suggestions")
                        st.markdown("*Get personalized advice from Google's Gemini AI to improve your resume*")
                        
                        with st.spinner("Gemini AI is analyzing your resume..."):
                            context = {
                                'resume_text': resume_text[:3000],
                                'job_role': job_role if job_role else "Based on Job Description",
                                'matched_skills': skill_match['matched_skills'][:10],
                                'missing_skills': skill_match['missing_skills'][:10],
                                'ats_score': ats_results['total_score'],
                                'section_scores': section_scores
                            }
                            
                            ai_response = llm_assistant.get_resume_feedback(context)
                            st.markdown(f'<div class="ai-suggestion">{ai_response}</div>', unsafe_allow_html=True)
                    else:
                        st.info("💡 **Enable AI Suggestions**: Add your Gemini API key in the sidebar to get AI-powered resume improvement suggestions!")

elif page == "🤖 AI Resume Assistant":
    st.title("🤖 AI Resume Assistant")
    st.markdown("Chat with Gemini AI to improve your resume, get personalized advice, and ask questions")
    
    # Check if API key is configured
    if not llm_assistant.has_valid_key():
        st.warning("⚠️ Gemini API Key Required")
        st.info("""
        **To use the AI Resume Assistant, please:**
        1. Add your Gemini API key in the sidebar
        2. Get a free key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        3. The key is free and gives you 60 requests per minute
        
        *Once you add the key, refresh the page or click the button below.*
        """)
        if "placeholder" in llm_assistant.get_key_status_message().lower():
            st.error("The current `GEMINI_API_KEY` in `.env` looks like a sample key. Replace it with a real key from Google AI Studio.")
        
        if st.button("🔄 Check Again", use_container_width=True):
            st.rerun()
    else:
        # Check if resume is uploaded
        if not st.session_state.resume_text:
            st.warning("⚠️ Please upload and analyze a resume first in the 'Resume Analyzer' tab")
            
            uploaded_file = st.file_uploader(
                "Quick Upload - Choose your resume (PDF or DOCX)",
                type=['pdf', 'docx'],
                key="quick_upload"
            )
            
            if uploaded_file:
                with st.spinner("Processing resume..."):
                    resume_text = extract_resume_text(uploaded_file)
                    if resume_text:
                        st.session_state.resume_text = resume_text
                        st.success("✅ Resume loaded! You can now chat with the AI assistant.")
                        st.rerun()
        else:
            # Display resume context
            with st.expander("📄 Current Resume Context", expanded=False):
                st.text(st.session_state.resume_text[:500] + "...")
                if st.session_state.analysis_results:
                    st.info(f"**ATS Score:** {st.session_state.analysis_results['ats_score']}%")
                    st.info(f"**Matched Skills:** {len(st.session_state.analysis_results.get('matched_skills', []))}")
                    st.info(f"**Missing Skills:** {len(st.session_state.analysis_results.get('missing_skills', []))}")
            
            # Chat interface
            st.markdown("### 💬 Chat with Gemini AI")
            st.caption("Powered by Google's Gemini 2.5 Flash model")
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message">👤 <b>You:</b><br>{message["content"]}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message">🤖 <b>Gemini AI:</b><br>{message["content"]}</div>', 
                               unsafe_allow_html=True)
            
            # Quick action buttons
            st.markdown("### 🚀 Quick Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📝 Rewrite Summary", use_container_width=True):
                    prompt = "Please rewrite my professional summary to be more impactful and ATS-friendly"
                    st.session_state.chat_history.append({'role': 'user', 'content': prompt})
                    
                    with st.spinner("Gemini AI is rewriting your summary..."):
                        context = {
                            'resume_text': st.session_state.resume_text,
                            'analysis_results': st.session_state.analysis_results,
                            'request': prompt
                        }
                        response = llm_assistant.chat_with_resume(prompt, context)
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.rerun()
            
            with col2:
                if st.button("💪 Strengthen Bullet Points", use_container_width=True):
                    prompt = "Please help me strengthen my work experience bullet points using stronger action verbs and quantifiable achievements"
                    st.session_state.chat_history.append({'role': 'user', 'content': prompt})
                    
                    with st.spinner("Gemini AI is strengthening your bullet points..."):
                        context = {
                            'resume_text': st.session_state.resume_text,
                            'analysis_results': st.session_state.analysis_results,
                            'request': prompt
                        }
                        response = llm_assistant.chat_with_resume(prompt, context)
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.rerun()
            
            with col3:
                if st.button("🎯 Tailor for Role", use_container_width=True):
                    if st.session_state.analysis_results:
                        job_role = st.session_state.analysis_results.get('job_role', 'your target role')
                        prompt = f"Please help me tailor my resume specifically for the {job_role} position. What keywords and skills should I emphasize?"
                        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
                        
                        with st.spinner("Gemini AI is tailoring your resume..."):
                            context = {
                                'resume_text': st.session_state.resume_text,
                                'job_role': job_role,
                                'analysis_results': st.session_state.analysis_results,
                                'request': prompt
                            }
                            response = llm_assistant.chat_with_resume(prompt, context)
                            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                        st.rerun()
                    else:
                        st.error("Please analyze your resume first")
            
            with col4:
                if st.button("📊 Improve ATS Score", use_container_width=True):
                    prompt = "What specific changes can I make to improve my ATS score? List top 5 actionable items."
                    st.session_state.chat_history.append({'role': 'user', 'content': prompt})
                    
                    with st.spinner("Gemini AI is analyzing improvements..."):
                        context = {
                            'resume_text': st.session_state.resume_text,
                            'ats_score': st.session_state.analysis_results['ats_score'] if st.session_state.analysis_results else None,
                            'request': prompt
                        }
                        response = llm_assistant.chat_with_resume(prompt, context)
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.rerun()
            
            st.markdown("---")
            
            # Chat input
            user_input = st.text_area("💬 Ask Gemini AI about your resume:", 
                                      placeholder="Example: How can I better highlight my leadership experience? What skills should I add for a data science role? Can you rewrite my project description?",
                                      height=100)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📤 Send Message", use_container_width=True):
                    if user_input:
                        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                        
                        with st.spinner("Gemini AI is thinking..."):
                            context = {
                                'resume_text': st.session_state.resume_text,
                                'analysis_results': st.session_state.analysis_results,
                                'request': user_input
                            }
                            response = llm_assistant.chat_with_resume(user_input, context)
                            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Tips for better results
            with st.expander("💡 Tips for better AI responses"):
                st.markdown("""
                - **Be specific** about which section you want help with
                - **Ask for examples** to see before/after comparisons
                - **Request multiple versions** for the same section
                - **Specify the job role** for tailored advice
                - **Ask about industry standards** for your field
                - **Paste specific sentences** you want to improve
                - **Gemini 2.5 Flash** is optimized for fast, quality responses
                """)

else:  # Resume Builder page
    st.title("📝 Resume Builder")
    st.markdown("Create a professional resume by filling out the form below")
    
    with st.form("resume_builder_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email *", placeholder="john.doe@example.com")
            phone = st.text_input("Phone", placeholder="+1 234 567 8900")
            linkedin = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/johndoe")
            github = st.text_input("GitHub URL", placeholder="https://github.com/johndoe")
        
        with col2:
            professional_summary = st.text_area(
                "Professional Summary",
                placeholder="Write a brief professional summary highlighting your key strengths and career goals...\n\nExample: Results-driven software engineer with 5+ years of experience in full-stack development...",
                height=150
            )
            
            education = st.text_area(
                "Education",
                placeholder="Bachelor of Science in Computer Science, Stanford University, 2020-2024\nGPA: 3.8/4.0\nRelevant Courses: Data Structures, Machine Learning, Cloud Computing",
                height=150
            )
        
        st.markdown("### Technical Skills")
        skills = st.text_area(
            "Skills (comma separated)",
            placeholder="Python, JavaScript, React, SQL, Git, Docker, AWS, Machine Learning, TensorFlow, Node.js",
            height=100,
            help="List your technical skills separated by commas"
        )
        
        st.markdown("### Work Experience")
        experience = st.text_area(
            "Experience (One entry per line)",
            placeholder="Software Engineer | Tech Corp | 2022-Present\n• Developed features serving 1M+ users\n• Improved application performance by 40%\n• Led team of 3 developers\n\nData Analyst | Data Inc | 2020-2022\n• Analyzed data for 100+ clients\n• Created automated reporting system saving 20 hours/week",
            height=200,
            help="Format: Title | Company | Duration\n• Achievement 1\n• Achievement 2"
        )
        
        st.markdown("### Projects")
        projects = st.text_area(
            "Projects (One entry per line)",
            placeholder="E-Commerce Platform | MERN Stack\n• Built full-stack app with 1000+ users\n• Implemented payment integration with Stripe\n• Reduced load time by 50% via optimization\n\nML Image Classifier | Python, TensorFlow\n• Achieved 95% accuracy on test set\n• Deployed as web application using Flask",
            height=200,
            help="Format: Project Name | Technologies\n• Description/achievement"
        )
        
        st.markdown("### Certifications & Awards")
        certifications = st.text_area(
            "Certifications",
            placeholder="• AWS Certified Solutions Architect (2023)\n• Google Data Analytics Professional (2022)\n• Best Innovation Award 2023",
            height=100
        )
        
        submitted = st.form_submit_button("✨ Generate Professional Resume", use_container_width=True)
        
        if submitted:
            if not name or not email:
                st.error("Please fill in required fields (Name and Email)")
            else:
                with st.spinner("Generating your professional resume..."):
                    form_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'linkedin': linkedin,
                        'github': github,
                        'summary': professional_summary,
                        'education': education,
                        'skills': skills,
                        'projects': projects,
                        'experience': experience,
                        'certifications': certifications
                    }
                    
                    formatted_data = format_resume_data(form_data)
                    pdf_bytes = builder.generate_pdf(formatted_data)
                    
                    st.success("✅ Resume generated successfully!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download Resume (PDF)",
                            data=pdf_bytes,
                            file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("🤖 AI-Improve This Resume", use_container_width=True):
                            if llm_assistant.has_valid_key():
                                st.info("💡 **Tip:** Switch to 'AI Resume Assistant' tab for personalized improvement suggestions from Gemini AI!")
                            else:
                                st.info("💡 **Tip:** Add your Gemini API key in the sidebar to get AI-powered improvement suggestions!")
                            st.balloons()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Resume Analyzer & Builder - Powered by Google Gemini AI 🤖 | Using Gemini 2.5 Flash</p>",
    unsafe_allow_html=True
)

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📚 Resources
- [Get Gemini API Key](https://makersuite.google.com/app/apikey)
- [Resume Tips](https://www.indeed.com/career-advice/resumes-cover-letters)
- [ATS Optimization Guide](https://www.jobscan.co/blog/33-ats-resume-tips/)

### 🎯 Pro Tips
1. **Gemini 2.5 Flash** is optimized for quality responses
2. Upload PDF format for best results
3. Be specific in AI chat for better responses
4. Free tier: 60 requests per minute

### 🔧 Features
- ✅ ATS Score Calculation
- ✅ Skill Gap Analysis  
- ✅ Gemini AI Integration
- ✅ Resume Builder
- ✅ Interactive AI Chat
""")
