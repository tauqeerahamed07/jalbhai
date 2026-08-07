from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./jalrakshak_dev.db"  # overridden by .env in real use
    use_postgis: bool = False
    use_real_ml: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
