import re
from app.schemas.analysis import SkillExtractionResult, ScoringResult, AnalyzeResponse, MatchedSkill
from app.core.logging import get_logger
from app.services.reranker_service import validate_match
from app.core.skill_ontology import LLM_FAMILY, PYTHON_BACKEND_FAMILY, JS_BACKEND_FAMILY, CV_FAMILY, API_INTEGRATION_FAMILY, DB_SCHEMA_FAMILY, CLOUD_FAMILY, VECTOR_DB_FAMILY, DL_FAMILY

logger = get_logger(__name__)

def get_family(skill: str) -> set:
    skill_lower = skill.lower()
    for fam in [LLM_FAMILY, PYTHON_BACKEND_FAMILY, JS_BACKEND_FAMILY, CV_FAMILY, API_INTEGRATION_FAMILY, DB_SCHEMA_FAMILY, CLOUD_FAMILY, VECTOR_DB_FAMILY, DL_FAMILY]:
        if skill_lower in fam or any(skill_lower in k for k in fam):
            return fam
    return set()

def validate_and_refine_analysis(
    resume_text: str,
    jd_text: str,
    extraction_result: SkillExtractionResult,
    scoring_result: ScoringResult
) -> ScoringResult:
    """
    AI Reviewer Pass.
    Validates and refines the analysis to prevent false missing skills and sanitize score inflation.
    Mutates the scoring_result directly to reflect refined scores and skills.
    """
    resume_lower = resume_text.lower()
    
    all_missing = scoring_result.critical_gaps + scoring_result.recommended_improvements + scoring_result.optional_skills
    sentences = [s.strip() for s in re.split(r'[.!?\n]', resume_text) if len(s.strip()) > 20]
    
    refined_critical = []
    refined_recommended = []
    refined_optional = []
    
    for missing in all_missing:
        skill_lower = missing.skill.lower()
        
        # 1. Same ontology family exists?
        family = get_family(skill_lower)
        found_equivalent = None
        if family:
            for m in scoring_result.matched_skills:
                if (m.candidate_skill or "").lower() in family or (m.required_skill or "").lower() in family or (m.skill or "").lower() in family:
                    found_equivalent = m
                    break
                    
        if found_equivalent:
            logger.info(f"Validator: Removed missing skill '{missing.skill}' - found equivalent '{found_equivalent.candidate_skill or found_equivalent.skill}'")
            continue
            
        # 2 & 3. Semantic evidence exists? Cross encoder confirms?
        promoted = False
        # We only check sentences that at least contain one keyword from the skill to save cross-encoder calls
        keywords = [w for w in skill_lower.split() if len(w) > 3]
        for sentence in sentences:
            if skill_lower in sentence.lower() or (keywords and any(kw in sentence.lower() for kw in keywords)):
                conf_score = validate_match(missing.skill, sentence)
                if conf_score > 0.75:
                    logger.info(f"Validator: Promoted missing skill '{missing.skill}' to matched via cross-encoder. Evidence: {sentence[:30]}")
                    scoring_result.matched_skills.append(MatchedSkill(
                        skill=missing.skill,
                        required_skill=missing.skill,
                        candidate_skill=missing.skill,
                        category=missing.skill,
                        evidence=f"Validated semantic evidence: {sentence}",
                        match_type="EQUIVALENT",
                        confidence=conf_score
                    ))
                    promoted = True
                    break
                    
        if promoted:
            continue
            
        if missing.importance == "CRITICAL":
            refined_critical.append(missing)
        elif missing.importance == "IMPORTANT":
            refined_recommended.append(missing)
        else:
            refined_optional.append(missing)

    scoring_result.critical_gaps = refined_critical
    scoring_result.recommended_improvements = refined_recommended
    scoring_result.optional_skills = refined_optional
    scoring_result.missing_skills = refined_critical + refined_recommended + refined_optional

    # 2. Score Sanity Checking & Inflation Prevention
    
    # Rules:
    # If resume only lists skills: Maximum score 75
    # If no projects: Maximum score 70
    # If no deployment/API/database evidence: Production score must stay low (cap 65)
    
    has_projects = any(p.detected for p in extraction_result.project_experience)
    
    prod_evidence = False
    for m in scoring_result.matched_skills:
        cat = m.category.lower()
        ev = (m.evidence or "").lower()
        if any(x in cat or x in ev for x in ["api", "deploy", "database", "production", "cloud", "docker", "kubernetes", "aws", "gcp", "azure"]):
            prod_evidence = True
            break
            
    if not has_projects:
        if scoring_result.final_score > 70.0:
            logger.info(f"Validator: Capping score from {scoring_result.final_score} to 70 due to no projects.")
            scoring_result.final_score = 70.0
    elif not prod_evidence:
        if scoring_result.final_score > 65.0:
            logger.info(f"Validator: Capping score from {scoring_result.final_score} to 65 due to no production/deployment evidence.")
            scoring_result.final_score = 65.0
    elif len(extraction_result.project_experience) == 0 and len(scoring_result.matched_skills) > 0:
        if scoring_result.final_score > 75.0:
            logger.info(f"Validator: Capping score from {scoring_result.final_score} to 75 due to resume only listing skills.")
            scoring_result.final_score = 75.0
            
    # 3. Evidence Verification (Cleanup hallucinated skills with generic evidence)
    refined_matched = []
    for skill in scoring_result.matched_skills:
        # If evidence is just generic "Found python in resume", reduce confidence or remove if strictly bad.
        # Here we just keep it but might log a warning.
        evidence_lower = (skill.evidence or "").lower()
        if "generic" in evidence_lower or "found" in evidence_lower and len(evidence_lower) < 25:
            logger.warning(f"Validator: Weak evidence detected for {skill.candidate_skill}: {skill.evidence}")
            # Decrease the score impact of this skill slightly or mark it partial.
            if skill.match_type == "EXACT_MATCH":
                skill.match_type = "PARTIAL_MATCH"
        refined_matched.append(skill)
        
    scoring_result.matched_skills = refined_matched
    
    # 4. Confidence Calibration
    if not has_projects:
        if scoring_result.confidence and scoring_result.confidence.confidence_level == "HIGH":
            scoring_result.confidence.confidence_level = "MEDIUM"

    return scoring_result
