"""Application settings and runtime configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    openai_api_key: str = Field(default="", alias="OpenAI")
    llama_cloud_api_key: str = Field(default="", alias="LLAMA_CLOUD_API_KEY")
    huggingface_token: str = Field(default="", alias="token")

    fact_check_space: str = Field(default="IWIHSG/fact_check", alias="FACT_CHECK_SPACE")
    factuality_api_name: str = Field(default="/factuality_check", alias="FACT_CHECK_API_NAME")
    openai_model_name: str = Field(default="gpt-4o", alias="OPENAI_MODEL_NAME")

    db_path: Path = Field(
        default_factory=lambda: project_root() / "all_talks.db",
        alias="ALL_TALKS_DB",
    )
    db_table_name: str = Field(default="filtered_speakerdeckfeatures", alias="DB_TABLE_NAME")

    model_mlp_path: Path = Field(
        default_factory=lambda: project_root() / "mlp_ensemble.sav", alias="MLP_MODEL_PATH"
    )
    model_svr_path: Path = Field(
        default_factory=lambda: project_root() / "svr.sav",
        alias="SVR_MODEL_PATH",
    )
    model_rfr_path: Path = Field(
        default_factory=lambda: project_root() / "rfr_embeddings.sav", alias="RFR_MODEL_PATH"
    )


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
