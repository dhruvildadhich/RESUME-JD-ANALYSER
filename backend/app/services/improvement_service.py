"""
Improvement Service.

Generates concrete, skill-targeted resume improvement suggestions
based on the list of missing skills.

Unlike generic tips ("Learn testing"), this service produces:
  - Specific action-verb sentences the candidate can paste into their resume
  - Prioritised by skill importance (CRITICAL > IMPORTANT > OPTIONAL)
  - Grounded in the actual JD requirement context
"""
from typing import List

from app.core.constants import (
    IMPORTANCE_CRITICAL,
    IMPORTANCE_IMPORTANT,
    IMPORTANCE_OPTIONAL,
)
from app.core.logging import get_logger
from app.schemas.analysis import MissingSkill, ImprovementSuggestion

logger = get_logger(__name__)

# Template library for common skill domains
_TEMPLATES: dict = {
    # Testing
    "pytest": "Add testing section: 'Implemented unit tests using pytest for FastAPI services, achieving {coverage}% route coverage and validating API edge cases'",
    "unit test": "Add testing context: 'Wrote unit tests with pytest/unittest for {service} services, ensuring reliability across {count}+ test cases'",
    "testing": "Add testing experience: 'Developed integration and unit test suites using pytest, covering API endpoints and data pipeline correctness'",
    # Cloud
    "aws": "Add cloud section: 'Deployed {service} on AWS EC2/Lambda with S3 storage, leveraging IAM roles for secure resource access'",
    "gcp": "Add GCP context: 'Deployed ML models and APIs on Google Cloud Platform using Cloud Run and Cloud Storage'",
    "azure": "Add Azure context: 'Deployed containerized applications on Azure App Service with Azure DevOps CI/CD pipelines'",
    "cloud": "Add cloud context: 'Deployed application to cloud infrastructure (AWS/GCP/Azure) with auto-scaling and load balancing configuration'",
    # Containers / DevOps
    "kubernetes": "Add orchestration: 'Orchestrated microservices deployment using Kubernetes, managing pod scaling and service discovery across {count} services'",
    "docker": "Add containerization: 'Containerized FastAPI/Node services using Docker with multi-stage builds, reducing image size by {pct}%'",
    "ci/cd": "Add DevOps: 'Configured CI/CD pipelines using GitHub Actions, automating test, build, and deployment stages on each PR merge'",
    "github actions": "Add CI/CD: 'Implemented GitHub Actions workflows for automated testing, Docker image builds, and deployment to production'",
    # Databases
    "postgresql": "Add database detail: 'Designed PostgreSQL schema with {count}+ tables, optimized queries with indexes, achieving sub-100ms response times'",
    "mongodb": "Add NoSQL context: 'Designed MongoDB collections and aggregation pipelines for {usecase}, handling {count}+ documents'",
    "redis": "Add caching detail: 'Implemented Redis caching layer for API responses, reducing database load by {pct}% and improving latency'",
    "vector database": "Add vector DB: 'Integrated vector database (FAISS/Pinecone/Weaviate) for semantic search, indexing {count}+ embeddings for retrieval'",
    # ML / AI
    "machine learning": "Add ML context: 'Built and evaluated ML models ({algorithm}) for {usecase}, achieving {metric}% accuracy on test set'",
    "pytorch": "Add PyTorch: 'Implemented neural network model using PyTorch for {usecase}, training on {dataset} and achieving {metric} performance'",
    "tensorflow": "Add TensorFlow: 'Developed and trained deep learning model using TensorFlow/Keras for {usecase} classification'",
    "langchain": "Add LangChain: 'Built LangChain pipeline integrating LLM with vector retrieval for context-aware responses in {usecase}'",
    "rag": "Add RAG detail: 'Implemented RAG pipeline using embedding model + vector DB retrieval, improving answer accuracy by grounding LLM in document context'",
    # Web frameworks
    "fastapi": "Add API detail: 'Built FastAPI REST API with Pydantic validation, JWT authentication, and async endpoint handling for {usecase}'",
    "django": "Add Django detail: 'Developed Django application with ORM models, REST API using DRF, and admin interface for {usecase}'",
    "flask": "Add Flask detail: 'Built Flask API with blueprint-based routing, SQLAlchemy ORM integration, and JWT authentication'",
    "react": "Add React detail: 'Built React frontend with component-based architecture, Redux state management, and API integration for {usecase}'",
    # System design
    "microservices": "Add architecture: 'Designed microservices architecture splitting monolith into {count} independent services, each with its own database and API contract'",
    "system design": "Add system design: 'Designed distributed system for {usecase} with horizontal scaling, load balancing, and fault-tolerant message queuing'",
    # Monitoring
    "monitoring": "Add observability: 'Implemented application monitoring using Prometheus/Grafana, setting up dashboards and alerts for API latency and error rates'",
    "logging": "Add logging: 'Structured logging with Python logging/ELK stack, enabling distributed tracing and error monitoring in production'",
}


def _find_template(skill_name: str) -> str:
    """Find the best matching template for a skill name."""
    skill_lower = skill_name.lower().strip()

    # Exact match
    if skill_lower in _TEMPLATES:
        return _TEMPLATES[skill_lower]

    # Partial match (skill name contained in template key)
    for key, template in _TEMPLATES.items():
        if key in skill_lower or skill_lower in key:
            return template

    # Generic fallback
    return (
        f"Add {skill_name} context: 'Implemented {skill_name} for [your project/service], "
        f"demonstrating hands-on production usage and measurable impact'"
    )


def _build_suggestion(missing: MissingSkill) -> str:
    """Generate a concrete improvement suggestion for a missing skill."""
    # If Gemini already provided a good suggestion, use it (enhanced)
    existing = (missing.suggestion or "").strip()
    if existing and len(existing) > 30:
        return existing

    # Use the note/reason if available
    context = (missing.reason or missing.note or "").strip()

    template = _find_template(missing.skill)

    # Replace placeholder tokens with sensible defaults
    suggestion = (
        template
        .replace("{service}", "the primary API service")
        .replace("{coverage}", "85")
        .replace("{count}", "50")
        .replace("{pct}", "40")
        .replace("{usecase}", "the target use case")
        .replace("{algorithm}", "Random Forest / XGBoost")
        .replace("{dataset}", "training dataset")
        .replace("{metric}", "92")
    )

    if context:
        suggestion = f"{suggestion}. Note: {context}"

    return suggestion


def generate_improvements(
    critical_gaps: List[MissingSkill],
    recommended_improvements: List[MissingSkill],
    optional_skills: List[MissingSkill],
) -> List[ImprovementSuggestion]:
    """
    Generate a prioritized list of actionable resume improvement suggestions.

    Args:
        critical_gaps: CRITICAL missing skills.
        recommended_improvements: IMPORTANT missing skills.
        optional_skills: OPTIONAL missing skills.

    Returns:
        List of ImprovementSuggestion ordered by priority (CRITICAL first).
    """
    suggestions: List[ImprovementSuggestion] = []

    all_missing = [
        (IMPORTANCE_CRITICAL, critical_gaps),
        (IMPORTANCE_IMPORTANT, recommended_improvements),
        (IMPORTANCE_OPTIONAL, optional_skills),
    ]

    for priority, skill_list in all_missing:
        for missing in skill_list:
            suggestion_text = _build_suggestion(missing)
            suggestions.append(ImprovementSuggestion(
                missing_skill=missing.skill,
                suggestion=suggestion_text,
                priority=priority,
            ))

    logger.info(
        "Improvement plan generated",
        extra={
            "total_suggestions": len(suggestions),
            "critical_count": len(critical_gaps),
            "important_count": len(recommended_improvements),
            "optional_count": len(optional_skills),
        },
    )

    return suggestions
