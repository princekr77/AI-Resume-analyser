# AI Resume Analyzer & Enhancer

A Streamlit-based web application that analyzes resumes using Google Gemini AI and provides ATS compatibility scores, strengths, missing skills, and actionable improvement suggestions.

## Features

- **Resume Upload** — Supports PDF and DOCX formats
- **AI Analysis** — Powered by Google Gemini 2.0 Flash
- **ATS Score** — Compatibility score out of 100 with detailed breakdown
- **Key Strengths** — Highlights what's working well in your resume
- **Missing Skills** — Identifies gaps for your target role
- **Improvement Suggestions** — Actionable steps to enhance your resume

## Project Structure

```
Gen-Ai/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── utils/
    ├── __init__.py
    ├── parser.py            # Resume text extraction (PDF/DOCX)
    ├── analyzer.py          # Gemini AI analysis & prompt engineering
    └── ui_components.py     # Reusable Streamlit UI components
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

**Option A:** Create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your key
```

**Option B:** Enter the key directly in the app sidebar.

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Usage

1. Enter your **Gemini API key** in the sidebar (or set it in `.env`)
2. **Upload** your resume (PDF or DOCX)
3. Enter the **target job role**
4. Click **Analyze Resume**
5. Review your ATS score, strengths, missing skills, and suggestions

## Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Google Gemini API** — AI-powered analysis
- **PyPDF2** — PDF text extraction
- **python-docx** — DOCX text extraction
## 🚀 How to Run the Project

1. Install dependencies:
pip install -r requirements.txt

2. Run the app:
streamlit  run app.py
## ✨ Additional Features
- Clean & Interactive UI with custom Streamlit theme  
- Secure API Key handling using `.env` file support  
- Fast resume processing and instant AI feedback  
- Supports multiple job role targeting for better customization  
- Beginner-friendly project structure for easy understanding  

## 📊 Analysis Output Includes
- Overall ATS Score (0–100)  
- Resume Formatting Review  
- Keyword Optimization Check  
- Skills Matching with Target Role  
- Content Quality Suggestions  
- Professional Summary Feedback  

## 🛠 Future Improvements
- Resume Download after Enhancement  
- Cover Letter Generator  
- LinkedIn Profile Analyzer  
- Multiple Resume Comparison  
- Job Description Matching Score  
- Dark Mode UI Enhancements  

## 📌 Why This Project?
This project helps job seekers improve their resumes using AI-driven insights. It increases the chances of passing ATS systems used by companies and makes resumes stronger for recruiters.

## 👨‍💻 Author
Developed by Rudra Pratap Singh using Python, Streamlit, and Google Gemini AI.
