"""
Skill Ontology Core Module.

Contains all hardcoded mappings, taxonomy definitions, and canonical normalizations
used by both the local extraction engine and as hints for the LLM extraction.
"""

CANONICAL_CASES = {
    "python": "Python",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "docker": "Docker",
    "docker compose": "Docker Compose",
    "kubernetes": "Kubernetes",
    "gemini": "Gemini",
    "openai": "OpenAI",
    "claude": "Claude",
    "groq": "Groq",
    "mistral": "Mistral",
    "llama": "Llama",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "chromadb": "ChromaDB",
    "pinecone": "Pinecone",
    "faiss": "FAISS",
    "weaviate": "Weaviate",
    "qdrant": "Qdrant",
    "rag": "RAG",
    "llm": "LLM",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "scikit-learn": "Scikit-learn",
    "pandas": "Pandas",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "pytest": "Pytest",
    "ci/cd": "CI/CD"
}

# --- Families ---

LLM_FAMILY = {
    "llm", "large language model", "openai", "chatgpt", "gpt", "gemini", "claude", 
    "llama", "mistral", "groq", "hugging face", "transformers", "deepseek", 
    "anthropic", "cohere", "vertex ai"
}

PYTHON_BACKEND_FAMILY = {"fastapi", "flask", "django"}

JS_BACKEND_FAMILY = {"express", "nodejs", "node.js", "nest.js", "nestjs", "express.js"}

DL_FAMILY = {"tensorflow", "pytorch", "keras", "scikit-learn", "sklearn"}

VECTOR_DB_FAMILY = {"chromadb", "chroma", "pinecone", "faiss", "weaviate", "qdrant", "milvus"}

CV_FAMILY = {
    "computer vision", "cv", "opencv", "virtual try-on", "image processing", 
    "multimodal ai", "visual recommendation", "yolo", "image segmentation", 
    "image classification", "object detection"
}

CLOUD_FAMILY = {"aws", "gcp", "azure", "google cloud", "amazon web services", "cloud deployment"}

API_INTEGRATION_FAMILY = {
    "rest api", "gemini api", "groq api", "cloudinary api", "third-party api", 
    "third-party apis", "external services", "api integration"
}

DB_SCHEMA_FAMILY = {
    "database schema design", "mongodb models", "mongoose schemas", 
    "entity relationships", "database architecture", "mongodb", "postgresql", 
    "mysql", "mongoose models", "sqlalchemy models", "schema design", "mongoose odm", "mongoose"
}

RAG_FAMILY = {
    "rag", "retrieval augmented generation", "chunking", "embedding generation", 
    "semantic search", "retrieval pipeline", "document qa", "langchain", "llamaindex"
}

DEVOPS_FAMILY = {
    "docker", "docker compose", "kubernetes", "ci/cd", "cloud deployment", "github actions"
}

TESTING_FAMILY = {
    "pytest", "unit testing", "integration testing", "testing", "tdd", "jest"
}

ALL_FAMILIES = {
    "LLM API Integration": LLM_FAMILY,
    "Python Backend Development": PYTHON_BACKEND_FAMILY,
    "JavaScript Backend Development": JS_BACKEND_FAMILY,
    "Deep Learning": DL_FAMILY,
    "Vector Database Experience": VECTOR_DB_FAMILY,
    "Computer Vision": CV_FAMILY,
    "Cloud Infrastructure": CLOUD_FAMILY,
    "API Integration": API_INTEGRATION_FAMILY,
    "Database Schema Design": DB_SCHEMA_FAMILY,
    "RAG Implementation": RAG_FAMILY,
    "DevOps": DEVOPS_FAMILY,
    "Testing": TESTING_FAMILY
}

COMMON_SKILLS = list(
    LLM_FAMILY | PYTHON_BACKEND_FAMILY | JS_BACKEND_FAMILY | DL_FAMILY | 
    VECTOR_DB_FAMILY | CV_FAMILY | CLOUD_FAMILY | API_INTEGRATION_FAMILY | 
    DB_SCHEMA_FAMILY | RAG_FAMILY | DEVOPS_FAMILY | TESTING_FAMILY
) + [
    "python", "pandas", "embeddings", "vector database", 
    "rest api", "graphql", "microservices", "machine learning", "deep learning", 
    "nlp", "data science", "agile", "scrum", "java", "c++", "rust", "go", 
    "ruby", "php", "swift", "kotlin", "sql", "html", "css", "spring", "react", 
    "vue", "angular", "git", "github", "gitlab", "jenkins", "terraform", "ansible", 
    "redis", "elasticsearch", "sqlite", "dynamodb", "multer", "nodemailer", 
    "socket.io", "react router", "axios"
]

CATEGORY_MAPPINGS = {
    "gemini": "LLM API Integration",
    "openai": "LLM API Integration",
    "claude": "LLM API Integration",
    "groq": "LLM API Integration",
    "mistral": "LLM API Integration",
    "llama": "LLM API Integration",
    "chromadb": "Vector Database Experience",
    "pinecone": "Vector Database Experience",
    "faiss": "Vector Database Experience",
    "weaviate": "Vector Database Experience",
    "qdrant": "Vector Database Experience",
    "sentencetransformer": "Embedding Experience",
    "embeddings": "Embedding Experience",
    "fastapi": "Python Backend Development",
    "flask": "Python Backend Development",
    "django": "Python Backend Development",
    "express": "JavaScript Backend Development",
    "node.js": "JavaScript Backend Development",
    "nodejs": "JavaScript Backend Development",
    "nest.js": "JavaScript Backend Development",
    "multer": "JavaScript Backend Development",
    "nodemailer": "JavaScript Backend Development",
    "socket.io": "JavaScript Backend Development",
    "react": "Frontend Development",
    "next.js": "Frontend Development",
    "nextjs": "Frontend Development",
    "react router": "Frontend Development",
    "axios": "API Integration",
    "rest api": "API Integration",
    "docker": "DevOps",
    "docker compose": "DevOps",
    "kubernetes": "DevOps",
    "ci/cd": "DevOps",
    "pytorch": "Deep Learning",
    "tensorflow": "Deep Learning",
    "keras": "Deep Learning",
    "scikit-learn": "Machine Learning",
    "mongoose odm": "Database Schema Design",
    "mongoose": "Database Schema Design",
    "mongodb models": "Database Schema Design",
    "pytest": "Testing",
    "unit testing": "Testing",
    "integration testing": "Testing"
}

IMPORTANCE_MAPPINGS = {
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
    "groq": "OPTIONAL"
}
