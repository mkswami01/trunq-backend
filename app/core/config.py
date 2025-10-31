from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "Trunq Backend"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Database
    supabase_url: str = ""
    supabase_anon_key: str = ""

    # OpenAI
    openai_api_key: str = ""

    # Security
    secret_key: str = "change-this-in-production"

    supermemory_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
