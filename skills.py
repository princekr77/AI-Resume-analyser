"""
Job role skill database for resume analysis
Contains predefined skills for various job roles
"""

JOB_ROLES_SKILLS = {
    "Game Developer": {
        "required_skills": [
            "Unity", "Unreal Engine", "C#", "C++", "3D Modeling",
            "Game Physics", "Animation", "Shader Programming", "OpenGL",
            "DirectX", "Mobile Game Development", "VR/AR", "Game Design",
            "Version Control", "Debugging"
        ],
        "keywords": ["game", "unity", "unreal", "3d", "animation", "physics"]
    },
    
    "Web Developer": {
        "required_skills": [
            "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js",
            "Node.js", "Python", "Django", "Flask", "MongoDB", "PostgreSQL",
            "MySQL", "RESTful API", "GraphQL", "Git", "AWS", "Docker",
            "Responsive Design", "Web Performance"
        ],
        "keywords": ["web", "frontend", "backend", "fullstack", "api", "database"]
    },
    
    "Data Analyst": {
        "required_skills": [
            "Python", "SQL", "Excel", "Tableau", "Power BI", "Pandas",
            "NumPy", "Statistics", "Data Visualization", "Data Cleaning",
            "Machine Learning", "R", "SAS", "SPSS", "Business Intelligence",
            "Data Mining", "Reporting", "Analytics"
        ],
        "keywords": ["data", "analytics", "analysis", "statistics", "visualization", "reporting"]
    },
    
    "Data Scientist": {
        "required_skills": [
            "Python", "R", "SQL", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "Scikit-learn", "Statistics", "NLP",
            "Computer Vision", "Data Visualization", "Big Data", "Hadoop",
            "Spark", "Cloud Computing", "Feature Engineering", "A/B Testing"
        ],
        "keywords": ["machine learning", "deep learning", "ai", "statistics", "algorithm", "modeling"]
    },
    
    "AI/ML Engineer": {
        "required_skills": [
            "Python", "TensorFlow", "PyTorch", "Scikit-learn", "Keras",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "Data Structures", "Algorithms", "Cloud Computing", "AWS/GCP/Azure",
            "Docker", "Kubernetes", "MLflow", "Apache Spark", "SQL"
        ],
        "keywords": ["machine learning", "deep learning", "artificial intelligence", "neural networks", "nlp"]
    },
    
    "DevOps Engineer": {
        "required_skills": [
            "Linux", "AWS/Azure/GCP", "Docker", "Kubernetes", "Jenkins",
            "CI/CD", "Terraform", "Ansible", "Python", "Bash", "Git",
            "Monitoring Tools", "Prometheus", "Grafana", "Networking",
            "Security", "Infrastructure as Code"
        ],
        "keywords": ["devops", "infrastructure", "cloud", "automation", "ci/cd", "deployment"]
    },
    
    "Full Stack Developer": {
        "required_skills": [
            "JavaScript", "React/Angular/Vue", "Node.js", "Python/Django",
            "MongoDB", "PostgreSQL", "HTML5", "CSS3", "REST API", "Git",
            "AWS", "Docker", "GraphQL", "TypeScript", "Express.js",
            "Responsive Design", "Authentication"
        ],
        "keywords": ["fullstack", "frontend", "backend", "database", "api", "cloud"]
    },
    
    "Software Engineer": {
        "required_skills": [
            "Java", "Python", "C++", "Data Structures", "Algorithms",
            "Design Patterns", "System Design", "Git", "SQL", "Testing",
            "Agile", "Scrum", "Object-Oriented Programming", "Debugging",
            "Code Review", "Documentation"
        ],
        "keywords": ["software development", "programming", "algorithms", "system design", "testing"]
    },
    
    "Product Manager": {
        "required_skills": [
            "Product Strategy", "Market Research", "User Stories", "Agile",
            "Scrum", "Roadmapping", "Data Analysis", "Communication",
            "Leadership", "Wireframing", "MVP Development", "User Testing",
            "Stakeholder Management", "Business Metrics", "Competitive Analysis"
        ],
        "keywords": ["product", "management", "roadmap", "stakeholder", "agile", "scrum"]
    },
    
    "UI/UX Designer": {
        "required_skills": [
            "Figma", "Adobe XD", "Sketch", "User Research", "Wireframing",
            "Prototyping", "User Interface Design", "User Experience",
            "Visual Design", "Interaction Design", "HTML/CSS", "Responsive Design",
            "Usability Testing", "Design Systems", "Accessibility"
        ],
        "keywords": ["ui", "ux", "design", "user experience", "interface", "prototyping"]
    }
}

def get_all_job_roles():
    """Return list of all available job roles"""
    return list(JOB_ROLES_SKILLS.keys())

def get_skills_for_role(role):
    """Get required skills for a specific job role"""
    return JOB_ROLES_SKILLS.get(role, {}).get("required_skills", [])

def get_keywords_for_role(role):
    """Get keywords for a specific job role"""
    return JOB_ROLES_SKILLS.get(role, {}).get("keywords", [])