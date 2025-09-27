import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # Base directories
    BASE_DIR = Path(__file__).parent.absolute()
    DATA_DIR = BASE_DIR / "data"
    KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
    SCHEMAS_DIR = DATA_DIR / "schemas"
    UPLOADS_DIR = DATA_DIR / "uploads"
    MODELS_DIR = BASE_DIR / "models"

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "amtly-demo-secret-key")

    # App settings
    DEBUG = True

    # Language settings
    SUPPORTED_LANGUAGES = ['en', 'de']
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # Default to English now
    FALLBACK_LANGUAGE = "en"

    # Language-specific settings
    LANGUAGE_NAMES = {
        'en': 'English',
        'de': 'Deutsch',
        'ar': 'العربية',
        'fr': 'Français',
        'es': 'Español',
        'it': 'Italiano',
        'tr': 'Türkçe',
        'ru': 'Русский'
    }

    # AI settings
    OPENAI_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.3

    # File upload settings
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}

    # Vector store settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Database settings
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATA_DIR}/amtly.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def create_directories(cls):
        """Create all necessary directories"""
        directories = [
            cls.DATA_DIR,
            cls.KNOWLEDGE_BASE_DIR,
            cls.KNOWLEDGE_BASE_DIR / "documents",
            cls.KNOWLEDGE_BASE_DIR / "chunks",
            cls.KNOWLEDGE_BASE_DIR / "embeddings",
            cls.SCHEMAS_DIR,
            cls.UPLOADS_DIR,
            cls.MODELS_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def is_supported_language(cls, lang_code):
        """Check if language is supported"""
        return lang_code in cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_language_name(cls, lang_code):
        """Get display name for language"""
        return cls.LANGUAGE_NAMES.get(lang_code, lang_code.upper())