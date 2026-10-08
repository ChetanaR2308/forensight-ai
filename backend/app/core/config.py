from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ForenSight AI MVP"
    environment: str = "development"
    jwt_secret: str = "change-me-local-dev-only"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    max_upload_size_mb: int = 25
    uploads_dir: str = "backend/uploads"
    cors_origins: str = "http://localhost:5173"
    use_mongo: bool = False
    mongo_uri: str = "mongodb://mongodb:27017"
    mongo_db_name: str = "forensight"
    enable_llm: bool = False
    demo_admin_password: str = "admin123"
    demo_investigator_password: str = "investigator123"
    demo_analyst_password: str = "analyst123"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
