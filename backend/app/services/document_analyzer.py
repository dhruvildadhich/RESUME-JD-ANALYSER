import re
from typing import Dict

def parse_resume_sections(text: str) -> Dict[str, str]:
    """
    Parses a resume text into logical sections based on common headings.
    Returns a dictionary of section names to text content.
    """
    sections = {
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "certifications": "",
        "general": ""
    }
    
    current_section = "general"
    lines = text.split("\n")
    
    for line in lines:
        lower = line.strip().lower()
        
        # Determine if the line is a section heading
        if re.match(r'^(skills|technical skills|technologies|core competencies)', lower) and len(lower) < 50:
            current_section = "skills"
        elif re.match(r'^(experience|work experience|employment|professional experience)', lower) and len(lower) < 50:
            current_section = "experience"
        elif re.match(r'^(projects|academic projects|personal projects)', lower) and len(lower) < 50:
            current_section = "projects"
        elif re.match(r'^(education|academic background)', lower) and len(lower) < 50:
            current_section = "education"
        elif re.match(r'^(certifications|licenses|awards)', lower) and len(lower) < 50:
            current_section = "certifications"
        else:
            sections[current_section] += line + "\n"
            
    # Clean up empty sections and return
    return {k: v.strip() for k, v in sections.items() if v.strip()}


def parse_jd_sections(text: str) -> Dict[str, str]:
    """
    Parses a job description text into logical sections based on common headings.
    Returns a dictionary of section names to text content.
    """
    sections = {
        "skills": "",
        "responsibilities": "",
        "qualifications": "",
        "preferred_skills": "",
        "experience_requirements": "",
        "general": ""
    }
    
    current_section = "general"
    lines = text.split("\n")
    
    for line in lines:
        lower = line.strip().lower()
        
        # Determine if the line is a section heading
        if re.match(r'^(skills|required skills|technologies|requirements|core requirements)', lower) and len(lower) < 50:
            current_section = "skills"
        elif re.match(r'^(responsibilities|what you will do|duties|your role)', lower) and len(lower) < 50:
            current_section = "responsibilities"
        elif re.match(r'^(qualifications|about you|who you are|basic qualifications)', lower) and len(lower) < 50:
            current_section = "qualifications"
        elif re.match(r'^(preferred skills|bonus points|nice to have|preferred qualifications)', lower) and len(lower) < 50:
            current_section = "preferred_skills"
        elif re.match(r'^(experience|experience requirements)', lower) and len(lower) < 50:
            current_section = "experience_requirements"
        else:
            sections[current_section] += line + "\n"
            
    # Clean up empty sections and return
    return {k: v.strip() for k, v in sections.items() if v.strip()}
