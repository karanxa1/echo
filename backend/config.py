import os
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('config.env')

class Settings:
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./echo.db")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Lowercase aliases for compatibility
    secret_key = SECRET_KEY
    algorithm = ALGORITHM
    access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    API_HOST: str = os.getenv("API_HOST", "localhost")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # File upload settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")

settings = Settings() 