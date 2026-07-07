"""
Local Skill Extraction Service (Fallback).

Contains rule-based technical skill extraction, categorization, and seniority evaluation
for use when the Gemini API is unavailable or as a post-processing step.
"""
import re
from typing import Any, Final

from app.core.constants import (
    IMPORTANCE_CRITICAL,
    IMPORTANCE_IMPORTANT,
    IMPORTANCE_OPTIONAL,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
    EQUIVALENT,
    PARTIAL,
)
from app.schemas.analysis import SkillExtractionResult, MatchedSkill, MissingSkill, ProjectExperience, CandidateLevel, ConfidenceResult
from app.core.logging import get_logger

logger = get_logger(__name__)

_CANONICAL_CASES = {
    "python": "Python",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "gemini": "Gemini",
    "openai": "OpenAI",
    "claude": "Claude",
    "groq": "Groq",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "chromadb": "ChromaDB",
    "pinecone": "Pinecone",
    "faiss": "FAISS",
    "weaviate": "Weaviate",
    "rag": "RAG",
    "llm": "LLM",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "scikit-learn": "Scikit-learn",
    "pandas": "Pandas"
}

LLM_FAMILY = {
    "llm", "large language model", "openai", "chatgpt", "gpt", "gemini", "claude", 
    "llama", "mistral", "groq", "hugging face", "transformers", "deepseek", 
    "anthropic", "cohere", "vertex ai"
}
BACKEND_FAMILY = {"fastapi", "flask", "django", "express", "nodejs", "node.js", "spring"}
DL_FAMILY = {"tensorflow", "pytorch", "keras", "scikit-learn", "sklearn"}
VECTOR_DB_FAMILY = {"chromadb", "chroma", "pinecone", "faiss", "weaviate", "qdrant", "milvus"}
CV_FAMILY = {
    "computer vision", "cv", "opencv", "virtual try-on", "image processing", 
    "multimodal ai", "visual recommendation", "yolo", "image segmentation", 
    "image classification", "object detection"
}

_COMMON_SKILLS = list(LLM_FAMILY) + list(BACKEND_FAMILY) + list(DL_FAMILY) + list(VECTOR_DB_FAMILY) + list(CV_FAMILY) + [
    "python", "rag", "langchain", "llamaindex", "docker", "kubernetes", "chunking", 
    "embeddings", "vector database", "retrieval pipeline", "testing", "pytest", 
    "scikit-learn", "pandas", "rest api", "graphql", "microservices", "ci/cd", 
    "machine learning", "deep learning", "nlp", "computer vision", "data science", 
    "agile", "scrum", "tdd", "java", "c++", "rust", "go", "ruby", "php", "swift", "kotlin", 
    "sql", "html", "css", "spring", "react", "vue", "angular", "express", "node.js", 
    "git", "github", "gitlab", "jenkins", "terraform", "ansible", "aws", "gcp", "azure",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "dynamodb"
]

_CATEGORY_MAPPINGS = {
    "gemini": "LLM API Integration",
    "openai": "LLM API Integration",
    "claude": "LLM API Integration",
    "groq": "LLM API Integration",
    "chromadb": "Vector Database Experience",
    "pinecone": "Vector Database Experience",
    "faiss": "Vector Database Experience",
    "weaviate": "Vector Database Experience",
    "sentencetransformer": "Embedding Experience",
    "embeddings": "Embedding Experience",
    "fastapi": "Python Backend Development",
    "flask": "Python Backend Development",
    "django": "Python Backend Development",
    "react": "Frontend Development",
    "next.js": "Frontend Development",
    "nextjs": "Frontend Development",
    "docker": "Containerization",
    "kubernetes": "Containerization",
    "pytorch": "Deep Learning",
    "tensorflow": "Deep Learning",
    "keras": "Deep Learning",
    "scikit-learn": "Machine Learning"
}

_IMPORTANCE_MAPPINGS = {
    "python": "CRITICAL",
    "fastapi": "CRITICAL",
    "flask": "CRITICAL",
    "django": "CRITICAL",
    "llm": "CRITICAL",
    "rag": "CRITICAL",
    "embeddings": "CRITICAL",
    "chromadb": "CRITICAL",
    "pinecone": "CRITICAL",
    "faiss": "CRITICAL",
    "weaviate": "CRITICAL",
    "rest api": "CRITICAL",
    "backend": "CRITICAL",
    "deep learning": "CRITICAL",
    "pytorch": "CRITICAL",
    "tensorflow": "CRITICAL",
    
    "docker": "IMPORTANT",
    "langchain": "IMPORTANT",
    "llamaindex": "IMPORTANT",
    "sql": "IMPORTANT",
    "cloud": "IMPORTANT",
    "testing": "IMPORTANT",
    "ci/cd": "IMPORTANT",
    "mlops": "IMPORTANT",
    "containerization": "IMPORTANT",
    
    "claude": "OPTIONAL",
    "openai": "OPTIONAL",
    "azure": "OPTIONAL",
    "aws": "OPTIONAL",
    "gcp": "OPTIONAL",
    "research": "OPTIONAL"
}

ACTION_VERBS = {
    "built", "designed", "implemented", "optimized", "deployed", "integrated", 
    "architected", "developed", "automated", "created", "engineered", "managed",
    "led", "pioneered", "orchestrated", "scaled"
}


def _find_evidence_sentence(resume_text: str, keyword: str) -> str:
    """Finds a context sentence in the resume containing the keyword."""
    # Split by periods, newlines, etc.
    sentences = re.split(r'[.\n\r]', resume_text)
    for s in sentences:
        # Use word boundary to match whole words and ignore case
        if re.search(r"\b" + re.escape(keyword.lower()) + r"\b", s.lower()):
            cleaned = s.strip()
            # Limit to reasonable length
            if 15 <= len(cleaned) <= 180:
                return cleaned
    return f"Demonstrated capability in {keyword.title()} in resume projects."


def extract_all_resume_keywords(text: str) -> set[str]:
    text_lower = text.lower()
    found = set()
    # List of keywords for matching
    keywords = list(LLM_FAMILY) + list(BACKEND_FAMILY) + list(DL_FAMILY) + list(VECTOR_DB_FAMILY) + list(CV_FAMILY) + [
        "python", "rag", "langchain", "llamaindex", "docker", "kubernetes", "chunking", 
        "embeddings", "vector database", "retrieval pipeline", "testing", "pytest", 
        "scikit-learn", "pandas", "rest api", "graphql", "microservices", "ci/cd", 
        "machine learning", "deep learning", "nlp", "computer vision", "data science", 
        "agile", "scrum", "tdd"
    ]
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower) or kw in text_lower: # 'in text_lower' for multi-word keywords
            found.add(kw)
    return found


def detect_pdf_issues(text: str) -> bool:
    words = text.split()
    if not words:
        return True
    
    # Check for unusually high percentage of single-letter "words"
    single_letters = sum(1 for w in words if len(w) == 1 and w.lower() not in ("a", "i", "o", "x")) # Added 'x' for common placeholders
    if (single_letters / len(words)) > 0.10:
        logger.warning(f"High single-letter word count detected: {single_letters/len(words):.2f}")
        return True
        
    # Check for very short documents that might indicate parsing issues or empty content
    if len(words) < 100 and len(text) < 500: # Combined word and char count for robustness
        logger.warning(f"Document too short: {len(words)} words, {len(text)} characters")
        return True
        
    # Check for excessive non-alphanumeric characters (could indicate parsing artifacts)
    non_alphanum_chars = sum(1 for char in text if not char.isalnum() and not char.isspace())
    if (non_alphanum_chars / len(text)) > 0.20: # If more than 20% of chars are non-alphanumeric (excluding spaces)
        logger.warning(f"High non-alphanumeric character count: {non_alphanum_chars/len(text):.2f}")
        return True

    return False


def find_evidence_for_family(resume_text: str, family_members_found: list[str]) -> str:
    evidences = []
    # Prioritize evidence with action verbs
    for member in family_members_found:
        sentences = re.split(r'[.\n\r]', resume_text)
        for s in sentences:
            if re.search(r"\b" + re.escape(member.lower()) + r"\b", s.lower()):
                cleaned = s.strip()
                if any(verb in cleaned.lower() for verb in ACTION_VERBS) and 15 <= len(cleaned) <= 180:
                    evidences.append(cleaned)
                    if len(evidences) >= 2:
                        return " | ".join(evidences)
    
    # If no action verb evidence, take any relevant sentence
    for member in family_members_found:
        sent = _find_evidence_sentence(resume_text, member)
        if sent and "Demonstrated capability" not in sent:
            evidences.append(sent)
            if len(evidences) >= 2:
                break
    if evidences:
        return " | ".join(evidences)
    if family_members_found:
        return f"Demonstrated capability in {_CANONICAL_CASES.get(family_members_found[0], family_members_found[0].title())} in resume projects."
    return "Candidate has experience with related technologies."


def extract_years_of_experience(text: str) -> float | None:
    text_lower = text.lower()
    
    # Pattern 1: X+ years experience
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience", text_lower)
    if matches:
        try:
            return max(float(m) for m in matches)
        except ValueError:
            pass

    # Pattern 2: Start and end years of employment
    years = re.findall(r"\b(20\d{2})\b", text_lower)
    if years:
        try:
            year_ints = sorted([int(y) for y in years if 1990 <= int(y) <= 2026]) # Filter for reasonable year range
            
            # If "present" or "current" is mentioned, assume current year for max
            current_year = 2026
            if any(x in text_lower for x in ["present", "current", "to date", "now"]):
                max_y = current_year
            elif year_ints:
                max_y = max(year_ints)
            else:
                max_y = current_year
            
            if len(year_ints) > 1:
                min_y = min(year_ints)
                span = max_y - min_y
                if 0 < span < 30: # Max reasonable career span
                    return float(span)
            elif len(year_ints) == 1: # Only one year mentioned, e.g., "2023 - Present" where "Present" wasn't caught
                span = current_year - year_ints[0] + 1 # +1 to count the current year
                if 0 < span < 5: # If only one year, assume short experience, but not for very long periods
                    return float(span)
        except Exception as e:
            logger.warning(f"Error parsing years from dates: {e}", exc_info=False)
            
    # Check for explicit "Student" or "Intern" indicators
    if any(x in text_lower for x in ["student", "internship", "intern", "undergrad", "bachelor", "master", "phd", "university", "college", "academic research"]):
        return 0.5 # Default for student/intern, indicating very limited experience (0-1 years)

    # If no specific experience is found, return None
    return None


def evaluate_seniority(text: str) -> tuple[str, str]:
    text_lower = text.lower()
    
    is_student_or_intern = any(x in text_lower for x in [
        "student", "internship", "intern", "pursuing", "undergrad", "b.e", "b.tech", "bachelor",
        "master's student", "phd candidate", "research assistant", "academic project"
    ])
    
    years = extract_years_of_experience(text)
    
    level_map = {
        "Student": (0, 0.9),
        "Junior AI Engineer": (1, 2.9),
        "Mid Level AI Engineer": (3, 4.9),
        "Senior AI Engineer": (5, 999) # Arbitrarily high for 5+
    }
    
    # Check for ownership, architecture, leadership keywords
    ownership_keywords = ["architected", "designed", "led", "managed", "mentor", "team lead", "technical lead", "principal"]
    has_ownership_evidence = any(kw in text_lower for kw in ownership_keywords)
    
    production_keywords = ["production", "deployed", "scalable", "high-performance", "ci/cd", "monitoring", "observability"]
    has_production_evidence = any(kw in text_lower for kw in production_keywords)
    
    complexity_keywords = ["complex systems", "distributed systems", "large-scale", "optimization", "novel algorithms"]
    has_complexity_evidence = any(kw in text_lower for kw in complexity_keywords)
    
    # Adjust years for student roles if clearly an intern despite high year count (e.g., student worked for 5 years total, but all internships)
    # Ensure years is not None before performing arithmetic
    if years is not None and is_student_or_intern and years > 3:
        years = max(years * 0.5, 1.0) # Reduce effective years for long student careers, but ensure at least 1 year

    determined_level = "Entry Level AI Engineer" # Default if nothing else matches
    reason_parts = []

    if is_student_or_intern:
        determined_level = "AI Engineer Intern Candidate"
        reason_parts.append("Candidate is an intern/student.")
    elif years is None:
        determined_level = "Entry Level AI Engineer"
        reason_parts.append("Could not confidently determine years of professional experience from the resume. Classified as entry level.")
    elif years < 2:
        determined_level = "Junior AI Engineer"
        reason_parts.append(f"Candidate has less than 2 years of professional experience ({(years if years is not None else 0.0):.1f} years detected).")
    elif 2 <= years < 5:
        determined_level = "Mid Level AI Engineer"
        reason_parts.append(f"Candidate has {(years if years is not None else 0.0):.1f} years of professional experience, demonstrating independent execution on technical projects.")
    else: # 5+ years
        determined_level = "Senior AI Engineer"
        reason_parts.append(f"Candidate has {(years if years is not None else 0.0):.1f}+ years of professional experience, with signs of architectural ownership and production impact.")

    strength_indicators = []
    if has_ownership_evidence:
        strength_indicators.append("strong ownership")
    if has_production_evidence:
        strength_indicators.append("production exposure")
    if has_complexity_evidence:
        strength_indicators.append("experience with complex systems")

    if strength_indicators:
        strength_str = ", ".join(strength_indicators)
        reason_parts.append(f"Demonstrates {strength_str}.")
    else:
        reason_parts.append("Limited explicit evidence of architectural ownership or significant production impact.")

    final_reason = " ".join(reason_parts).strip()
    return determined_level, final_reason


def calculate_confidence(fallback_mode: bool, pdf_issues: bool, weak_evidence: bool, jd_clarity_score: float = 1.0) -> tuple[int, str]:
    base_score = 100.0 # Max confidence
    
    if fallback_mode:
        base_score -= 20 # Significant confidence reduction if falling back to heuristics
        
    if pdf_issues:
        base_score -= 15 # PDF parsing issues reduce confidence
        
    if weak_evidence:
        base_score -= 15 # Lack of concrete evidence in resume reduces confidence
        
    # JD clarity (1.0 = perfect, 0.0 = terrible). Reduce confidence if JD is unclear
    base_score *= jd_clarity_score 
        
    # Cap score
    score = max(0, min(99, int(base_score)))
            
    if score >= 85:
        level = CONFIDENCE_HIGH
    elif score >= 60:
        level = CONFIDENCE_MEDIUM
    else:
        level = CONFIDENCE_LOW
        
    return score, level


def post_process_extraction_result(
    result: SkillExtractionResult,
    resume_text: str,
    jd_text: str
) -> SkillExtractionResult:
    resume_lower = resume_text.lower()
    # jd_lower = jd_text.lower() # Not used currently in post-processing, but useful for future
    
    resume_keywords = extract_all_resume_keywords(resume_text)
    pdf_issues = detect_pdf_issues(resume_text)
    
    def canonical_case(s: str) -> str:
        return _CANONICAL_CASES.get(s.lower(), s) # changed to s instead of s.title() for better preservation of case if not in canonical_cases
        
    new_matched = []
    # Process existing matched skills
    for m in result.matched_skills:
        m.skill = canonical_case(m.skill)
        m.category = _CATEGORY_MAPPINGS.get(m.skill.lower(), m.category or m.skill)
        if m.required_skill:
            m.required_skill = canonical_case(m.required_skill)
        if m.candidate_skill:
            m.candidate_skill = canonical_case(m.candidate_skill)
            
        # Ensure match_type is canonical
        if m.match_type == "EQUIVALENT_MATCH":
            m.match_type = "EQUIVALENT"
        elif m.match_type == "PARTIAL_MATCH":
            m.match_type = "PARTIAL"
            
        # Cap confidence at 0.95 and ensure a minimum of 0.25 (to avoid 0 confidence matches)
        m.confidence = min(0.95, max(0.25, m.confidence))
        new_matched.append(m)
        
    # Compile a set of original missing skills (flattening critical/recommended/optional)
    original_missing_skills_map = {ms.skill.lower(): ms for ms in result.missing_skills}
        
    # Also compile a set of all skills that were requested (either matched or missing)
    jd_requested_skills_lower = set()
    for m in result.matched_skills:
        req = m.required_skill or m.skill
        jd_requested_skills_lower.add(req.lower())
    for ms in result.missing_skills:
        jd_requested_skills_lower.add(ms.skill.lower())
        
    still_missing_categorized: dict[str, list] = {
        "CRITICAL": [],
        "IMPORTANT": [],
        "OPTIONAL": []
    }

    # Iterate over original missing skills to re-evaluate and potentially promote to matched
    for ms_name, ms_obj in original_missing_skills_map.items():
        # A. LLM family match check
        if ms_name in [("llm"), ("large language model"), ("llm api integration")]:
            candidate_llm_kws = [kw for kw in LLM_FAMILY if kw in resume_keywords]
            if candidate_llm_kws:
                cand_skill_parts = []
                if "llama" in resume_keywords:
                    cand_skill_parts.append("Llama")
                if "groq" in resume_keywords:
                    cand_skill_parts.append("Groq API")
                if "openai" in resume_keywords:
                    cand_skill_parts.append("OpenAI API")
                if "gemini" in resume_keywords:
                    cand_skill_parts.append("Gemini API")
                if "claude" in resume_keywords:
                    cand_skill_parts.append("Claude API")
                
                if not cand_skill_parts: # If specific LLMs not found, use general
                    cand_skill_parts = [canonical_case(x) for x in candidate_llm_kws[:2]] 
                cand_skill_str = " + ".join(cand_skill_parts) if cand_skill_parts else "Various LLMs"
                
                evidence_sent = find_evidence_for_family(resume_text, candidate_llm_kws)
                
                new_matched.append(
                    MatchedSkill(
                        skill="LLM API Integration",
                        required_skill=canonical_case(ms_obj.skill),
                        candidate_skill=cand_skill_str,
                        match_type=EQUIVALENT,
                        category="LLM API Integration",
                        evidence=f"Candidate demonstrates {cand_skill_str} experience through projects: {evidence_sent}",
                        confidence=0.90 # High confidence for strong evidence
                    )
                )
                continue # Skip adding to missing
                
        # B. Computer Vision match check
        if ms_name in [("computer vision"), ("cv")]:
            cv_found_kws = [kw for kw in CV_FAMILY if kw in resume_keywords]
            cv_tech = [x for x in cv_found_kws if x not in [("computer vision"), ("cv")]]
            if cv_tech:
                cand_skill = "Virtual Try-On Support" if "try-on" in resume_lower else canonical_case(cv_tech[0])
                evidence_sent = find_evidence_for_family(resume_text, cv_found_kws)
                new_matched.append(
                    MatchedSkill(
                        skill="Computer Vision",
                        required_skill=canonical_case(ms_obj.skill),
                        candidate_skill=cand_skill,
                        match_type=PARTIAL,
                        category="Computer Vision",
                        evidence=f"AI image workflow exposure through {cand_skill} implementation: {evidence_sent}",
                        confidence=0.70 # Medium confidence for partial match
                    )
                )
                continue # Skip adding to missing
                
        # C. Backend framework equivalency
        if ms_name in BACKEND_FAMILY:
            alt_found_kws = [kw for kw in BACKEND_FAMILY if kw in resume_keywords and kw != ms_name]
            if alt_found_kws:
                evidence_sent = find_evidence_for_family(resume_text, alt_found_kws)
                new_matched.append(
                    MatchedSkill(
                        skill="Python Backend Development",
                        required_skill=canonical_case(ms_obj.skill),
                        candidate_skill=canonical_case(alt_found_kws[0]),
                        match_type=EQUIVALENT,
                        category="Python Backend Development",
                        evidence=f"Equivalent backend experience: {evidence_sent}",
                        confidence=0.90
                    )
                )
                continue # Skip adding to missing
                
        # D. Vector DB equivalency
        if ms_name in VECTOR_DB_FAMILY:
            alt_found_kws = [kw for kw in VECTOR_DB_FAMILY if kw in resume_keywords and kw != ms_name]
            if alt_found_kws:
                evidence_sent = find_evidence_for_family(resume_text, alt_found_kws)
                new_matched.append(
                    MatchedSkill(
                        skill="Vector Database Experience",
                        required_skill=canonical_case(ms_obj.skill),
                        candidate_skill=canonical_case(alt_found_kws[0]),
                        match_type=EQUIVALENT,
                        category="Vector Database Experience",
                        evidence=f"Equivalent vector search: {evidence_sent}",
                        confidence=0.90
                    )
                )
                continue # Skip adding to missing
                
        # E. LLM API equivalency (specific providers)
        llm_api_kws = ["groq", "openai", "gemini", "claude"]
        if ms_name in [f"{kw} api" for kw in llm_api_kws] or ms_name in llm_api_kws:
            clean_ms_name = ms_name.replace(" api", "")
            alt_found_kws = [kw for kw in llm_api_kws if kw in resume_keywords and kw != clean_ms_name]
            if alt_found_kws:
                evidence_sent = find_evidence_for_family(resume_text, alt_found_kws)
                new_matched.append(
                    MatchedSkill(
                        skill="LLM API Integration",
                        required_skill=canonical_case(ms_obj.skill),
                        candidate_skill=canonical_case(alt_found_kws[0]),
                        match_type=EQUIVALENT,
                        category="LLM API Integration",
                        evidence=f"Equivalent LLM provider: {evidence_sent}",
                        confidence=0.90
                    )
                )
                continue # Skip adding to missing
                
        # F. Deep learning equivalency
        if ms_name in DL_FAMILY:
            alt_found_kws = [kw for kw in DL_FAMILY if kw in resume_keywords and kw != ms_name]
            if alt_found_kws:
                evidence_sent = find_evidence_for_family(resume_text, alt_found_kws)
                new_matched.append(
                    MatchedSkill(
                        skill="Deep Learning",
                        required_skill=canonical_case(ms_obj.skill),
                        candidate_skill=canonical_case(alt_found_kws[0]),
                        match_type=EQUIVALENT,
                        category="Deep Learning",
                        evidence=f"Equivalent deep learning framework: {evidence_sent}",
                        confidence=0.85 # Slightly lower for DL frameworks as they can differ
                    )
                )
                continue # Skip adding to missing
                
        # G. Custom RAG -> LangChain/LlamaIndex is Recommended Improvement (not Critical Gap)
        if ms_name in [("langchain"), ("llamaindex")]:
            if any(x in resume_lower for x in [("chunking"), ("embeddings"), ("vector database"), ("retrieval pipeline"), ("custom rag")]):
                ms_obj.importance = IMPORTANCE_IMPORTANT
                ms_obj.note = "Candidate has custom RAG pipeline experience, LangChain/LlamaIndex can be learned quickly."
                still_missing_categorized[IMPORTANCE_IMPORTANT].append(ms_obj)
                continue
                
        # H. Alternative LLM providers -> Optional (if generic LLM not matched but specific one is)
        if ms_name in [("openai"), ("gemini"), ("claude"), ("groq"), ("openai api"), ("gemini api"), ("claude api"), ("groq api")] and not any(m.category == "LLM API Integration" for m in new_matched):
             if any(kw in resume_keywords for kw in llm_api_kws): # Check if *any* LLM API is present
                ms_obj.importance = IMPORTANCE_OPTIONAL
                ms_obj.note = f"Candidate has alternative LLM tools/providers (e.g. {_CANONICAL_CASES.get(llm_api_kws[0], llm_api_kws[0].title())})."
                still_missing_categorized[IMPORTANCE_OPTIONAL].append(ms_obj)
                continue
        
        # I. Python completely missing -> Critical Gap
        if ms_name == "python":
            if "python" not in resume_keywords:
                ms_obj.importance = IMPORTANCE_CRITICAL
                ms_obj.note = "Python programming language is a critical gap for an AI Engineer role."
                still_missing_categorized[IMPORTANCE_CRITICAL].append(ms_obj)
                continue
        
        # Default fallback based on importance classification
        if ms_obj.importance == IMPORTANCE_CRITICAL:
            still_missing_categorized[IMPORTANCE_CRITICAL].append(ms_obj)
        elif ms_obj.importance == IMPORTANCE_IMPORTANT:
            still_missing_categorized[IMPORTANCE_IMPORTANT].append(ms_obj)
        else:
            still_missing_categorized[IMPORTANCE_OPTIONAL].append(ms_obj)

    result.critical_gaps = still_missing_categorized[IMPORTANCE_CRITICAL]
    result.recommended_improvements = still_missing_categorized[IMPORTANCE_IMPORTANT]
    result.optional_skills = still_missing_categorized["OPTIONAL"]
    result.missing_skills = result.critical_gaps + result.recommended_improvements + result.optional_skills
            
    # 4. Seniority Evaluation
    cand_level, reason = evaluate_seniority(resume_text)
    result.candidate_level = CandidateLevel(candidate_level=cand_level, reason=reason)
    
    # 5. Confidence Calculation
    # Re-evaluate weak evidence based on the new_matched list after post-processing
    generic_evidence_count = sum(
        1 for m in new_matched 
        if "Demonstrated capability" in m.evidence or len(m.evidence) < 25 or not any(verb in m.evidence.lower() for verb in ACTION_VERBS)
    )
    weak_evidence = (len(new_matched) == 0) or (generic_evidence_count / len(new_matched) > 0.4)
    
    # JD clarity cannot be assessed locally without a dedicated service. Assume perfect for now.
    conf_score, conf_level = calculate_confidence(
        fallback_mode=result.fallback_mode,
        pdf_issues=pdf_issues,
        weak_evidence=weak_evidence,
        jd_clarity_score=1.0 # Placeholder, to be implemented if JD parsing issues are detected
    )
    result.confidence = ConfidenceResult(confidence_score=conf_score, confidence_level=conf_level)
    
    result.matched_skills = new_matched
    
    return result

def extract_skills_fallback(resume_text: str, jd_text: str) -> SkillExtractionResult:
    """Fallback rule-based technical skill extraction when Gemini API is unavailable."""
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    # Find matching JD keywords
    jd_found = []
    for skill in _COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, jd_lower):
            jd_found.append(skill)

    if not jd_found:
        jd_found = ["python", "fastapi", "embeddings"] # Default critical skills if JD is empty or unparsable

    matched_skills: list[MatchedSkill] = []
    
    # Use maps for critical/recommended/optional
    critical_gaps_map = {}
    recommended_improvements_map = {}
    optional_skills_map = {}

    for jd_skill in jd_found:
        jd_category = _CATEGORY_MAPPINGS.get(jd_skill, jd_skill.title())
        importance = _IMPORTANCE_MAPPINGS.get(jd_skill, "IMPORTANT")

        has_skill = False
        evidence = ""
        match_type = "EXACT_MATCH"
        candidate_skill = _CANONICAL_CASES.get(jd_skill, jd_skill.title())

        # Direct match check
        pattern = r"\b" + re.escape(jd_skill) + r"\b"
        if re.search(pattern, resume_lower):
            has_skill = True
            sentence = _find_evidence_sentence(resume_text, jd_skill)
            evidence = 'Found \'' + _CANONICAL_CASES.get(jd_skill, jd_skill.title()) + '\' directly in the resume: "' + sentence + '"'
            match_type = "EXACT_MATCH"
        else:
            # Equivalent match check (same category)
            for res_skill in _COMMON_SKILLS:
                res_pattern = r"\b" + re.escape(res_skill) + r"\b"
                if re.search(res_pattern, resume_lower):
                    jd_cat = _CATEGORY_MAPPINGS.get(jd_skill.lower())
                    res_cat = _CATEGORY_MAPPINGS.get(res_skill.lower())
                    
                    if jd_cat and res_cat and res_cat == jd_cat:
                        has_skill = True
                        candidate_skill = _CANONICAL_CASES.get(res_skill, res_skill.title())
                        sentence = _find_evidence_sentence(resume_text, res_skill)
                        evidence = f"Found equivalent skill '{_CANONICAL_CASES.get(res_skill, res_skill.title())}' in resume matching '{_CANONICAL_CASES.get(jd_skill, jd_skill.title())}' (both map to {jd_cat}) in context: " + sentence
                        match_type = "EQUIVALENT"
                        break

        if has_skill:
            # Set individual skill match confidence
            skill_conf = 0.95 if match_type == "EXACT_MATCH" else 0.85
            # Decrease confidence if evidence is default/weak
            if "Demonstrated capability in" in evidence or not any(verb in evidence.lower() for verb in ACTION_VERBS):
                skill_conf -= 0.20
            skill_conf = max(0.25, skill_conf) # Ensure minimum confidence
            
            # Avoid adding duplicate skills if already matched through another equivalent
            if not any(m.required_skill and m.required_skill.lower() == jd_skill.lower() for m in matched_skills):
                    matched_skills.append(
                        MatchedSkill(
                            skill=jd_category,
                            required_skill=_CANONICAL_CASES.get(jd_skill, jd_skill.title()),
                            candidate_skill=candidate_skill,
                            match_type=match_type,
                            category=jd_category,
                            evidence=evidence,
                            confidence=skill_conf
                        )
                    )
        else:
            skill_display = _CANONICAL_CASES.get(jd_skill, jd_skill.title())
            note = f"Technology '{skill_display}' was not explicitly found in the resume."
            
            # Special handling for LLM providers if one is found, make others optional
            if jd_skill.lower() in LLM_FAMILY and any(kw in resume_lower for kw in LLM_FAMILY if kw != jd_skill.lower()):
                 note = f"Candidate has alternative LLM tools/providers. Learning {skill_display} is optional."
                 importance = "OPTIONAL"
            elif jd_skill.lower() == "python":
                if "python" not in resume_lower:
                    importance = "CRITICAL"
                    note = "Python programming language is a critical gap for an AI Engineer role."
            elif jd_skill.lower() in ["langchain", "llamaindex"] and any(x in resume_lower for x in ["chunking", "embeddings", "vector database", "retrieval pipeline"]):
                importance = "IMPORTANT"
                note = "Candidate has custom RAG pipeline experience, LangChain/LlamaIndex can be learned quickly."


            ms = MissingSkill(
                skill=_CANONICAL_CASES.get(jd_skill, jd_skill.title()),
                importance=importance,
                note=note
            )
            
            # Add to respective maps, avoiding duplicates
            if importance == "CRITICAL":
                critical_gaps_map[ms.skill.lower()] = ms
            elif importance == "IMPORTANT":
                recommended_improvements_map[ms.skill.lower()] = ms
            else:
                optional_skills_map[ms.skill.lower()] = ms

    # Convert maps back to lists
    critical_gaps = list(critical_gaps_map.values())
    recommended_improvements = list(recommended_improvements_map.values())
    optional_skills = list(optional_skills_map.values())
    missing_skills = critical_gaps + recommended_improvements + optional_skills

    # Detect high-level project experiences
    project_experiences = []
    experiences_to_check = {
        "RAG Pipeline Experience": ["rag", "chromadb", "pinecone", "weaviate", "vector", "retrieval pipeline", "custom rag"],
        "Vector Search Experience": ["chromadb", "pinecone", "faiss", "weaviate", "vector"],
        "LLM Integration Experience": ["gemini", "openai", "claude", "groq", "llm", "api"],
        "Fine-Tuning Experience": ["fine-tuning", "lora", "qlora", "peft", "model customization"],
        "Agentic Workflow Experience": ["agents", "crewai", "autogen", "langgraph", "multi-agent"]
    }

    for exp, keywords in experiences_to_check.items():
        detected = False
        evidence = ""
        found_keywords = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", resume_lower)]
        
        # If at least 2 keywords matched, or 1 strong keyword like 'rag' for RAG Pipeline
        if len(found_keywords) >= 2 or (len(found_keywords) >= 1 and exp == "RAG Pipeline Experience" and "rag" in found_keywords):
            detected = True
            # Find evidence sentence for first keyword
            kw_evidence = _find_evidence_sentence(resume_text, found_keywords[0])
            if "Demonstrated capability in" in kw_evidence: # Try to get better evidence if generic
                 kw_evidence = find_evidence_for_family(resume_text, found_keywords)

            evidence = f"Detected project design using {', '.join([_CANONICAL_CASES.get(k, k.title()) for k in found_keywords])}: " + kw_evidence

        if detected:
            project_experiences.append(
                ProjectExperience(
                    experience=exp,
                    evidence=evidence,
                    detected=True
                )
            )

    # Temporary placeholders; actual values will be set by post_process_extraction_result
    candidate_level = CandidateLevel(candidate_level="Junior Engineer", reason="Temporary evaluation by fallback.")
    confidence = ConfidenceResult(confidence_score=70, confidence_level="MEDIUM") # Default lower confidence for fallback

    result = SkillExtractionResult(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        critical_gaps=critical_gaps,
        recommended_improvements=recommended_improvements,
        optional_skills=optional_skills,
        project_experience=project_experiences,
        candidate_level=candidate_level,
        confidence=confidence,
        fallback_mode=True
    )
    
    try:
        result = post_process_extraction_result(result, resume_text, jd_text)
    except Exception as e:
        logger.error(f"Error post-processing fallback: {e}", exc_info=True)
        
    return result

