from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str
    jwt_secret: str = Field(min_length=32)
    access_token_minutes: int = Field(default=30, ge=1, le=1440)
    cors_origins: list[str] = ['http://localhost:5173']
    llm_api_key: str = ''
    llm_base_url: str = 'https://api.groq.com/openai/v1'
    llm_model: str = 'llama-3.3-70b-versatile'

    @field_validator('jwt_secret')
    @classmethod
    def secret_is_configured(cls, value):
        if value.startswith('REPLACE_'):
            raise ValueError('Generate a random JWT_SECRET before starting')
        return value

settings = Settings()
