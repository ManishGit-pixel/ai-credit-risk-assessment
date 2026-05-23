from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    USE_LOCAL_LLM: bool = True
    OPENAI_API_KEY: str = ""
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "loan_agent_db"
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # Risk Thresholds
    THRESHOLD_APPROVE: float = 0.4
    THRESHOLD_REJECT: float = 0.7
    
    # Plaid Configuration
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"  # sandbox, development, or production
    
    # Credit Bureau Mock API
    CREDIT_BUREAU_API_URL: str = "http://localhost:8001"
    CREDIT_BUREAU_API_KEY: str = "mock_api_key_12345"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
