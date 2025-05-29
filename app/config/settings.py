from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: int
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    TOKEN: str
    PAYMENT_TOKEN: str

    @property
    def get_url_postgres(self):
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
