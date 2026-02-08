from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
     
    model_config = SettingsConfigDict(env_file=".env", extra="ignore",case_sensitive=True)

    app_env: str = "local"
    app_name: str = "resilient-mobile-wallet"
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str="postgresql+asyncpg://postgres:postgres@db:5432/wallet"
    tb_cluster_id: int = 0
    tb_address: str = "tigerbeetle:3000"


settings = Settings()