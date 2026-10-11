from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:4200"
    admin_email: str = "admin@helpdesk.com"
    admin_password: str
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    mail_from: str = "HelpDesk <no-reply@helpdesk.com>"
    frontend_url: str = "http://localhost:4200"


settings = Settings()
