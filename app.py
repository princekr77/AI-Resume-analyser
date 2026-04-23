"""
Main Streamlit application for Resume Analyzer and Builder
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
from datetime import datetime

# Import custom modules
from parser import ResumeParser
from analyzer import ResumeAnalyzer
from skills import JOB_ROLES_SKILLS, get_all_job_roles, get_skills_for_role, get_keywords_for_role
from generator import ResumeBuilder, format_resume_data

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
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_analyzer():
    return ResumeAnalyzer()

@st.cache_resource
def init_builder():
    return ResumeBuilder()

analyzer = init_analyzer()
builder = init_builder()
parser = ResumeParser()

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Sidebar navigation
st.sidebar.title("📄 Navigation")
page = st.sidebar.radio(
    "Choose an option",
    ["📊 Resume Analyzer", "📝 Resume Builder"]
)

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

def display_score_card(score_dict):
    """Display ATS score in a card format"""
    total_score = score_dict['total_score']
    
    # Determine color based on score
    if total_score >= 80:
        color = "success-text"
        emoji = "🎉"
    elif total_score >= 60:
        color = "warning-text"
        emoji = "👍"
    else:
        color = "danger-text"
        emoji = "📈"
    
    # Main score
    st.markdown(f"""
    <div class="score-card">
        <h2>ATS Score: {total_score}% {emoji}</h2>
        <hr>
        <h4>Breakdown:</h4>
        <p>📊 Skill Match: {score_dict['skill_match_score']}% (50% weight)</p>
        <p>🔍 Keyword Relevance: {score_dict['keyword_score']}% (20% weight)</p>
        <p>📐 Resume Structure: {score_dict['structure_score']}% (20% weight)</p>
        <p>✅ Grammar Check: {score_dict['grammar_score']}% (10% weight)</p>
    </div>
    """, unsafe_allow_html=True)

# Main application logic
if page == "📊 Resume Analyzer":
    st.title("📊 Resume Analyzer")
    st.write("Upload your resume to get an ATS compatibility score and improvement suggestions.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX)",
            type=["pdf", "docx"],
            key="resume_upload"
        )
    
    with col2:
        job_title = st.selectbox(
            "Select Job Role",
            options=get_all_job_roles()
        )
    
    if uploaded_file is not None:
        # Extract text
        resume_text = extract_resume_text(uploaded_file)
        
        if resume_text:
            st.session_state.resume_text = resume_text
            
            # Run analysis
            if st.button("🔍 Analyze Resume", key="analyze_btn"):
                with st.spinner("Analyzing your resume..."):
                    results = analyzer.analyze_resume(resume_text, job_title)
                    st.session_state.analysis_done = True
                    st.session_state.analysis_results = results
                    st.rerun()
    
    # Display results
    if st.session_state.analysis_done and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.divider()
        st.subheader("Analysis Results")
        
        # Display score card
        display_score_card(results)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Skill Match", f"{results['skill_match_score']}%")
        with col2:
            st.metric("Keyword Match", f"{results['keyword_score']}%")
        with col3:
            st.metric("Structure Score", f"{results['structure_score']}%")
        with col4:
            st.metric("Grammar Score", f"{results['grammar_score']}%")
        
        # Recommendations
        st.subheader("📋 Recommendations")
        recommendations = results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.info("Great job! Your resume looks good.")
        
        # Matched and Missing skills
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Matched Skills")
            matched_skills = results.get('matched_skills', [])
            if matched_skills:
                for skill in matched_skills[:10]:
                    st.write(f"• {skill}")
            else:
                st.info("No specific skills matched. Consider adding more technical skills.")
        
        with col2:
            st.subheader("❌ Missing Skills")
            missing_skills = results.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills[:10]:
                    st.write(f"• {skill}")
            else:
                st.success("You have all the recommended skills!")
        
        # Export button
        if st.button("📥 Download Analysis Report"):
            st.info("Report download feature coming soon!")

elif page == "📝 Resume Builder":
    st.title("📝 Resume Builder")
    st.write("Create a professional resume tailored for your target role.")
    
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name", value="John Doe")
        email = st.text_input("Email", value="john@example.com")
        phone = st.text_input("Phone", value="+1 (555) 123-4567")
        location = st.text_input("Location", value="New York, NY")
    
    with col2:
        job_role = st.selectbox("Target Job Role", options=get_all_job_roles())
        years_exp = st.slider("Years of Experience", 0, 50, 5)
        education = st.text_input("Education", value="B.S. in Computer Science")
    
    # Skills section
    st.subheader("Skills")
    recommended_skills = get_skills_for_role(job_role)
    selected_skills = st.multiselect(
        "Select your skills",
        options=recommended_skills,
        default=recommended_skills[:5] if recommended_skills else []
    )
    
    # Experience section
    st.subheader("Work Experience")
    num_experiences = st.slider("Number of positions", 1, 5, 2)
    
    experiences = []
    for i in range(num_experiences):
        st.write(f"**Position {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input(f"Company {i+1}", value=f"Company {i+1}")
            title = st.text_input(f"Job Title {i+1}", value=f"Position {i+1}")
        with col2:
            start_date = st.text_input(f"Start Date {i+1}", value="01/2020")
            end_date = st.text_input(f"End Date {i+1}", value="Present")
        
        description = st.text_area(f"Description {i+1}", value="Describe your achievements and responsibilities")
        
        experiences.append({
            "company": company,
            "title": title,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        })
    
    # Generate resume
    if st.button("📄 Generate Resume", key="generate_btn"):
        with st.spinner("Generating your resume..."):
            resume_data = {
                "name": full_name,
                "email": email,
                "phone": phone,
                "location": location,
                "job_role": job_role,
                "years_exp": years_exp,
                "education": education,
                "skills": selected_skills,
                "experiences": experiences
            }
            
            # Generate PDF
            pdf_file = builder.build_resume(resume_data)
            
            st.success("Resume generated successfully!")
            st.download_button(
                label="📥 Download Resume (PDF)",
                data=pdf_file,
                file_name=f"{full_name}_Resume.pdf",
                mime="application/pdf"
            )