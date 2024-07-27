from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cez API"
    DESCRIPTION: str = "RestAPI of 'ituai.club', for the Cez game"
    VERSION: str = "0.0.1"

    class Config:
        env_file = ".env"

settings = Settings()
