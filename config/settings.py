"""
Configuration management for GitHub RAG Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    REPOSITORIES_DIR = DATA_DIR / "repositories"
    CHROMADB_DIR = DATA_DIR / "chromadb"
    
    # Model Settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence Transformers model
    GEMINI_MODEL = "gemini-2.5-flash"  # Gemini 2.5 Flash for answers
    
    # RAG Settings
    TOP_K_RESULTS = 5
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Embedding Settings
    # Embedding Settings (Ollama)
    OLLAMA_BASE_URL = "http://localhost:11434"
    EMBEDDING_MODEL = "nomic-embed-text"
    EMBEDDING_DIMENSION = 768
    
    # File Processing
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
        '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.css',
        '.sh', '.bash', '.sql', '.r', '.m', '.dart', '.vue', '.svelte'
    }
    
    MAX_FILE_SIZE_MB = 5
    
    # Ignored directories
    IGNORED_DIRS = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        'env', 'dist', 'build', '.next', '.nuxt', 'target',
        'bin', 'obj', 'vendor', 'bower_components', '.idea',
        '.vscode', '__MACOSX', '.DS_Store'
    }
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Create necessary directories
        cls.REPOSITORIES_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

# Validate settings on import
Settings.validate()