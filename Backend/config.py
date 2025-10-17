import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration management"""
    
    def __init__(self):
        # API Keys
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not self.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        
        # Feature flags
        self.LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        
        # Application settings
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
        self.CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
        self.ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.csv', '.md'}
        
        # RAG settings
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "4"))
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate required configuration"""
        # Create necessary directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.CHROMA_PERSIST_DIR, exist_ok=True)
        
        logger.info("Configuration loaded successfully")
        logger.info(f"Upload directory: {self.UPLOAD_DIR}")
        logger.info(f"Chroma directory: {self.CHROMA_PERSIST_DIR}")
        logger.info(f"Gemini API Key: {'Loaded' if self.GEMINI_API_KEY else 'Missing'}")

# Global configuration instance
config = Config()