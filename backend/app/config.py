"""Centralized application settings, loaded from environment variables / .env.

We only declare here what *our own* code reads directly (DB, storage paths, logging,
CORS, model choice). Anthropic and Langfuse credentials are also declared so
pydantic-settings validates they're present at startup, but note the underlying
SDKs (langchain-anthropic, langfuse) read ANTHROPIC_API_KEY / LANGFUSE_* straight
from os.environ themselves -- python-dotenv's load_dotenv() in main.py is what
makes that work, this Settings object doesn't have to hand those values to them.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # --- Anthropic / Claude ---
    anthropic_api_key: str
    anthropic_model: str = "claude-opus-5"

    # --- Langfuse ---
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # --- Database ---
    database_url: str

    # --- Storage (relative paths are resolved against backend/) ---
    upload_dir: Path = Path("storage/uploads")
    chart_dir: Path = Path("storage/charts")
    report_dir: Path = Path("storage/reports")

    # --- Logging ---
    log_level: str = "INFO"
    log_file: Path = Path("logs/app.log")

    # --- CORS ---
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def resolved_upload_dir(self) -> Path:
        return self._resolve(self.upload_dir)

    def resolved_chart_dir(self) -> Path:
        return self._resolve(self.chart_dir)

    def resolved_report_dir(self) -> Path:
        return self._resolve(self.report_dir)

    def resolved_log_file(self) -> Path:
        return self._resolve(self.log_file)

    def _resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else BACKEND_DIR / path


settings = Settings()
