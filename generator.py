"""
Resume builder and PDF generator module
"""

from typing import Dict, List
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

class ResumeBuilder:
    """Generate professional PDF resumes from user input"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style for name
        self.styles.add(ParagraphStyle(
            name='NameTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
            borderPadding=3,
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            leftIndent=0
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=4
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=3
        ))
    
    def generate_pdf(self, data: Dict) -> bytes:
        """
        Generate PDF resume from form data
        
        Args:
            data: Dictionary containing resume data
                {
                    'name': str,
                    'email': str,
                    'phone': str,
                    'education': List[Dict],
                    'skills': List[str],
                    'projects': List[Dict],
                    'experience': List[Dict]
                }
        
        Returns:
            PDF as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Name
        story.append(Paragraph(data.get('name', 'Your Name'), self.styles['NameTitle']))
        
        # Contact info
        contact_info = []
        if data.get('email'):
            contact_info.append(f"Email: {data['email']}")
        if data.get('phone'):
            contact_info.append(f"Phone: {data['phone']}")
        
        if contact_info:
            story.append(Paragraph(" | ".join(contact_info), self.styles['NormalText']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Education section
        if data.get('education'):
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            for edu in data['education']:
                edu_text = f"<b>{edu.get('degree', 'Degree')}</b>"
                if edu.get('institution'):
                    edu_text += f" - {edu['institution']}"
                if edu.get('year'):
                    edu_text += f" ({edu['year']})"
                if edu.get('gpa'):
                    edu_text += f" - GPA: {edu['gpa']}"
                
                story.append(Paragraph(edu_text, self.styles['NormalText']))
                if edu.get('description'):
                    story.append(Paragraph(edu['description'], self.styles['BulletPoint']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Skills section
        if data.get('skills'):
            story.append(Paragraph("TECHNICAL SKILLS", self.styles['SectionHeader']))
            skills_text = ", ".join(data['skills'])
            story.append(Paragraph(skills_text, self.styles['NormalText']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Experience section
        if data.get('experience'):
            story.append(Paragraph("WORK EXPERIENCE", self.styles['SectionHeader']))
            for exp in data['experience']:
                exp_title = f"<b>{exp.get('title', 'Position')}</b>"
                if exp.get('company'):
                    exp_title += f" at {exp['company']}"
                if exp.get('duration'):
                    exp_title += f" | {exp['duration']}"
                
                story.append(Paragraph(exp_title, self.styles['NormalText']))
                if exp.get('description'):
                    story.append(Paragraph(exp['description'], self.styles['BulletPoint']))
                if exp.get('achievements'):
                    achievements = exp['achievements'].split('\n')
                    for achievement in achievements:
                        if achievement.strip():
                            story.append(Paragraph(f"• {achievement.strip()}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Projects section
        if data.get('projects'):
            story.append(Paragraph("PROJECTS", self.styles['SectionHeader']))
            for project in data['projects']:
                project_title = f"<b>{project.get('name', 'Project')}</b>"
                if project.get('technologies'):
                    project_title += f" | {project['technologies']}"
                
                story.append(Paragraph(project_title, self.styles['NormalText']))
                if project.get('description'):
                    story.append(Paragraph(project['description'], self.styles['BulletPoint']))
                if project.get('link'):
                    story.append(Paragraph(f"Link: {project['link']}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

def format_resume_data(form_data: Dict) -> Dict:
    """
    Format form data into proper structure for PDF generation
    
    Args:
        form_data: Raw form data from Streamlit
        
    Returns:
        Formatted data dictionary
    """
    formatted = {
        'name': form_data.get('name', ''),
        'email': form_data.get('email', ''),
        'phone': form_data.get('phone', ''),
        'education': [],
        'skills': [],
        'projects': [],
        'experience': []
    }
    
    # Parse education (format: "Degree, Institution, Year, GPA, Description")
    education_text = form_data.get('education', '')
    if education_text:
        # Simple parsing - can be enhanced
        edu_entries = education_text.split('\n')
        for entry in edu_entries:
            if entry.strip():
                parts = [p.strip() for p in entry.split(',')]
                edu_dict = {
                    'degree': parts[0] if len(parts) > 0 else '',
                    'institution': parts[1] if len(parts) > 1 else '',
                    'year': parts[2] if len(parts) > 2 else '',
                    'gpa': parts[3] if len(parts) > 3 else '',
                    'description': parts[4] if len(parts) > 4 else ''
                }
                formatted['education'].append(edu_dict)
    
    # Parse skills (comma or newline separated)
    skills_text = form_data.get('skills', '')
    if skills_text:
        formatted['skills'] = [s.strip() for s in re.split(r'[,\n]+', skills_text) if s.strip()]
    
    # Parse projects (format: "Name,Technologies,Description,Link")
    projects_text = form_data.get('projects', '')
    if projects_text:
        proj_entries = projects_text.split('\n')
        for entry in proj_entries:
            if entry.strip():
                parts = [p.strip() for p in entry.split(',')]
                proj_dict = {
                    'name': parts[0] if len(parts) > 0 else '',
                    'technologies': parts[1] if len(parts) > 1 else '',
                    'description': parts[2] if len(parts) > 2 else '',
                    'link': parts[3] if len(parts) > 3 else ''
                }
                formatted['projects'].append(proj_dict)
    
    # Parse experience (format: "Title,Company,Duration,Description,Achievements")
    experience_text = form_data.get('experience', '')
    if experience_text:
        exp_entries = experience_text.split('\n')
        for entry in exp_entries:
            if entry.strip():
                parts = [p.strip() for p in entry.split(',')]
                exp_dict = {
                    'title': parts[0] if len(parts) > 0 else '',
                    'company': parts[1] if len(parts) > 1 else '',
                    'duration': parts[2] if len(parts) > 2 else '',
                    'description': parts[3] if len(parts) > 3 else '',
                    'achievements': parts[4] if len(parts) > 4 else ''
                }
                formatted['experience'].append(exp_dict)
    
    return formatted

import re  # Add this import