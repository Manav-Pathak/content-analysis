from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    local_database_url: str | None = None
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Docker is the primary workflow for this project.
        local_database_url is only used when you intentionally run the API
        outside Docker against the host-mapped Postgres port.
        """
        return self.local_database_url or self.database_url


# Single instance used across the app
settings = Settings()
