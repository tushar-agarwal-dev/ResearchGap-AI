import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchGap AI"
    VERSION: str = "3.0"
    API_V1_STR: str = ""
    
    # Database
    PGUSER: str = "tusharagarwal"
    DATABASE_PASSWORD: str = ""
    PGHOST: str = "localhost"
    PGPORT: str = "5432"
    PGDATABASE: str = "researchgap"
    DATABASE_URL: str = ""

    # Security
    JWT_SECRET: str = "researchgap-dev-secret"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_TTL_SECONDS: int = 60 * 60 * 24
    
    # LLM
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-latest" 
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        from urllib.parse import quote_plus
        if self.DATABASE_PASSWORD:
            auth = f"{quote_plus(self.PGUSER)}:{quote_plus(self.DATABASE_PASSWORD)}"
        else:
            auth = quote_plus(self.PGUSER)
        
        return f"postgresql+psycopg2://{auth}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"


settings = Settings()
