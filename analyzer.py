"""
Resume analysis module for skill extraction, scoring, and suggestions
"""

import re
from typing import Dict, List, Set, Tuple
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeAnalyzer:
    """Analyze resume content and generate scores"""
    
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            self.stop_words = set()
        self.weak_verbs = [
            'worked', 'did', 'made', 'handled', 'responsible for',
            'assisted', 'helped', 'contributed to', 'participated in'
        ]
        self.strong_verbs = [
            'developed', 'created', 'implemented', 'designed', 'architected',
            'led', 'managed', 'optimized', 'improved', 'increased', 'reduced',
            'achieved', 'delivered', 'launched', 'built', 'engineered'
        ]
    
    def extract_skills(self, text: str) -> Set[str]:
        """
        Extract skills from resume text using pattern matching
        
        Args:
            text: Resume text
            
        Returns:
            Set of extracted skills
        """
        text = text.lower()
        skills = set()
        
        # Common technical skills to look for
        common_skills = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'html', 'css', 'sql', 'mongodb', 'postgresql', 'mysql', 'git', 'docker',
            'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
            'numpy', 'tableau', 'power bi', 'excel', 'machine learning', 'deep learning',
            'nlp', 'computer vision', 'unity', 'unreal engine', 'c#', 'c++', 'php',
            'ruby', 'swift', 'kotlin', 'flutter', 'react native', 'graphql', 'rest api',
            'kubernetes', 'jenkins', 'terraform', 'ansible', 'linux', 'bash',
            'data analysis', 'statistics', 'project management', 'agile', 'scrum',
            'leadership', 'communication', 'problem solving', 'teamwork'
        }
        
        # Extract skills by matching common skills
        for skill in common_skills:
            if skill in text:
                skills.add(skill)
        
        # Extract skills using patterns (e.g., "Skills: Python, Java, SQL")
        skills_pattern = re.findall(r'(?:skills|technologies|expertise)[:\s]+([^\n]+)', text, re.IGNORECASE)
        for skills_line in skills_pattern:
            skill_items = re.split(r'[,|•·♦‣◦▪➢❯❱✦✧→•\n]+', skills_line)
            for item in skill_items:
                skill = item.strip().lower()
                if len(skill) > 1 and len(skill) < 30:
                    skills.add(skill)
        
        return skills
    
    def calculate_skill_match(self, resume_skills: Set[str], required_skills: List[str]) -> Dict:
        """
        Calculate skill match between resume and job requirements
        
        Args:
            resume_skills: Set of skills found in resume
            required_skills: List of required skills for the job
            
        Returns:
            Dictionary with match details
        """
        required_set = set(skill.lower() for skill in required_skills)
        matched = resume_skills.intersection(required_set)
        missing = required_set - resume_skills
        
        match_percentage = (len(matched) / len(required_set) * 100) if required_set else 0
        
        return {
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "match_percentage": round(match_percentage, 2),
            "total_required": len(required_set),
            "total_matched": len(matched)
        }
    
    def calculate_keyword_relevance(self, resume_text: str, job_description: str = None, 
                                  keywords: List[str] = None) -> float:
        """
        Calculate keyword relevance score
        
        Args:
            resume_text: Resume text
            job_description: Optional job description for advanced matching
            keywords: Optional list of keywords for role
            
        Returns:
            Keyword relevance score (0-100)
        """
        resume_lower = resume_text.lower()
        
        # If job description is provided, use TF-IDF similarity
        if job_description:
            vectorizer = CountVectorizer(stop_words='english', max_features=1000)
            try:
                vectors = vectorizer.fit_transform([resume_lower, job_description.lower()])
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                return similarity * 100
            except:
                pass
        
        # Otherwise use keyword matching
        if keywords:
            keywords_lower = [k.lower() for k in keywords]
            found_keywords = sum(1 for keyword in keywords_lower if keyword in resume_lower)
            return (found_keywords / len(keywords_lower)) * 100 if keywords_lower else 0
        
        return 50  # Default score
    
    def check_resume_structure(self, text: str) -> float:
        """
        Check if resume has good structure (sections, formatting, etc.)
        
        Args:
            text: Resume text
            
        Returns:
            Structure score (0-100)
        """
        score = 0
        text_lower = text.lower()
        
        # Essential sections to look for
        sections = {
            'experience': ['experience', 'work experience', 'work history', 'employment'],
            'education': ['education', 'academic', 'degree', 'university', 'college'],
            'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
            'projects': ['projects', 'personal projects', 'portfolio']
        }
        
        # Check for each section
        found_sections = 0
        for section, patterns in sections.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_sections += 1
                    break
        
        score += (found_sections / len(sections)) * 40  # 40% for sections
        
        # Check for contact information
        has_email = bool(re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text))
        has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text))
        if has_email or has_phone:
            score += 20  # 20% for contact info
        
        # Check for quantifiable achievements (numbers like %)
        has_numbers = bool(re.search(r'\d+%|\$\d+|\d+\s*(?:years|months)', text))
        if has_numbers:
            score += 20  # 20% for achievements
        
        # Check for action verbs
        has_action_verbs = any(verb in text_lower for verb in self.strong_verbs)
        if has_action_verbs:
            score += 20  # 20% for action verbs
        
        return min(score, 100)
    
    def check_grammar(self, text: str) -> float:
        """
        Basic grammar check (simplified for demonstration)
        
        Args:
            text: Resume text
            
        Returns:
            Grammar score (0-100)
        """
        score = 100
        lines = text.split('\n')
        
        # Check for common issues
        issues = 0
        
        # Check for run-on sentences (very long sentences)
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if len(sentence.split()) > 30:  # Too long
                issues += 1
        
        # Check for missing periods at end of lines
        for line in lines:
            line = line.strip()
            if line and not line[-1] in '.!?':
                issues += 0.5
        
        # Check for all caps sections (might be okay for headers)
        caps_lines = sum(1 for line in lines if line.isupper() and len(line) > 20)
        if caps_lines > 5:
            issues += 2
        
        # Calculate score
        score -= min(issues, 50) * 2
        
        return max(score, 0)
    
    def generate_suggestions(self, resume_skills: Set[str], matched_skills: List[str], 
                           missing_skills: List[str], resume_text: str) -> List[str]:
        """
        Generate improvement suggestions based on analysis
        """
        suggestions = []
        
        # Skill-based suggestions
        if missing_skills:
            suggestions.append(f"Add these missing skills to your resume: {', '.join(missing_skills[:5])}")
        
        if not matched_skills:
            suggestions.append("No matching skills found. Please add relevant technical skills to your resume.")
        
        # Action verb suggestions
        weak_verbs_found = [verb for verb in self.weak_verbs if verb in resume_text.lower()]
        if weak_verbs_found:
            suggestions.append(f"Replace weak action verbs like '{weak_verbs_found[0]}' with stronger alternatives (developed, implemented, optimized, etc.)")
        
        # Projects suggestion
        if 'projects' not in resume_text.lower():
            suggestions.append("Add a 'Projects' section to showcase practical applications of your skills")
        
        # Section suggestions
        missing_sections = []
        if 'experience' not in resume_text.lower():
            missing_sections.append("Work Experience")
        if 'education' not in resume_text.lower():
            missing_sections.append("Education")
        if 'skills' not in resume_text.lower():
            missing_sections.append("Skills")
        
        if missing_sections:
            suggestions.append(f"Add these essential sections: {', '.join(missing_sections)}")
        
        # Quantifiable achievements
        if not re.search(r'\d+%|\$\d+|\d+\s*(?:years|months|projects|clients)', resume_text.lower()):
            suggestions.append("Add quantifiable achievements (e.g., 'Increased sales by 30%') to stand out")
        
        # Formatting suggestions
        if len(resume_text.split()) < 300:
            suggestions.append("Your resume seems short. Add more details about your experience and projects.")
        elif len(resume_text.split()) > 1000:
            suggestions.append("Your resume is quite long. Consider condensing to 1-2 pages for better readability.")
        
        return suggestions
    
    def calculate_ats_score(self, skill_match: Dict, keyword_score: float, 
                          structure_score: float, grammar_score: float) -> Dict:
        """
        Calculate overall ATS score with weights
        
        Args:
            skill_match: Skill match dictionary
            keyword_score: Keyword relevance score
            structure_score: Structure score
            grammar_score: Grammar score
            
        Returns:
            Dictionary with score breakdown
        """
        weight_skills = 0.50  # 50% weight
        weight_keywords = 0.20  # 20% weight
        weight_structure = 0.20  # 20% weight
        weight_grammar = 0.10  # 10% weight
        
        total_score = (
            (skill_match['match_percentage'] * weight_skills) +
            (keyword_score * weight_keywords) +
            (structure_score * weight_structure) +
            (grammar_score * weight_grammar)
        )
        
        return {
            "total_score": round(total_score, 2),
            "skill_match_score": round(skill_match['match_percentage'], 2),
            "keyword_score": round(keyword_score, 2),
            "structure_score": round(structure_score, 2),
            "grammar_score": round(grammar_score, 2),
            "weights": {
                "skills": weight_skills * 100,
                "keywords": weight_keywords * 100,
                "structure": weight_structure * 100,
                "grammar": weight_grammar * 100
            }
        }

    def analyze_resume(self, resume_text: str, job_role: str, job_data: Dict = None) -> Dict:
        """
        Run the complete resume analysis flow expected by the Streamlit app.

        Args:
            resume_text: Extracted resume text
            job_role: Selected job role from the UI
            job_data: Optional override containing required_skills/keywords

        Returns:
            Dictionary with the full analysis payload used by the UI
        """
        if not resume_text or not resume_text.strip():
            return {
                "total_score": 0,
                "skill_match_score": 0,
                "keyword_score": 0,
                "structure_score": 0,
                "grammar_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "recommendations": ["No readable resume text was found. Please upload a text-based PDF or DOCX file."],
                "job_role": job_role,
                "word_count": 0
            }

        required_skills = []
        keywords = []

        if job_data:
            required_skills = job_data.get("required_skills", [])
            keywords = job_data.get("keywords", [])
        else:
            try:
                from skills import get_skills_for_role, get_keywords_for_role
                required_skills = get_skills_for_role(job_role)
                keywords = get_keywords_for_role(job_role)
            except Exception:
                required_skills = []
                keywords = []

        resume_skills = self.extract_skills(resume_text)
        skill_match = self.calculate_skill_match(resume_skills, required_skills)
        keyword_score = self.calculate_keyword_relevance(resume_text, keywords=keywords)
        structure_score = self.check_resume_structure(resume_text)
        grammar_score = self.check_grammar(resume_text)
        score_breakdown = self.calculate_ats_score(
            skill_match=skill_match,
            keyword_score=keyword_score,
            structure_score=structure_score,
            grammar_score=grammar_score
        )
        recommendations = self.generate_suggestions(
            resume_skills=resume_skills,
            matched_skills=skill_match["matched_skills"],
            missing_skills=skill_match["missing_skills"],
            resume_text=resume_text
        )

        return {
            **score_breakdown,
            "matched_skills": sorted(skill_match["matched_skills"]),
            "missing_skills": sorted(skill_match["missing_skills"]),
            "recommendations": recommendations,
            "extracted_skills": sorted(resume_skills),
            "job_role": job_role,
            "word_count": len(resume_text.split())
        }
