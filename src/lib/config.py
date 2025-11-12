"""Configuration management for WADE Vulnerability DDS.

Loads settings from environment variables and YAML files
per constitution's modular design principle.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field

# pydantic v2 splits BaseSettings into pydantic-settings; provide a fallback
try:
    from pydantic import BaseSettings  # type: ignore

    _HAS_BASE_SETTINGS = True
except Exception:
    BaseSettings = None  # type: ignore
    _HAS_BASE_SETTINGS = False


if _HAS_BASE_SETTINGS:

    class Settings(BaseSettings):
        """Application settings loaded from environment and config files."""

        model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

        # Database
        database_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/wade")

        # Redis
        redis_url: str = Field(default="redis://localhost:6379/0")

        # RabbitMQ / Celery
        rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672/")
        celery_broker_url: str = Field(default="amqp://guest:guest@localhost:5672/")
        celery_result_backend: str = Field(default="redis://localhost:6379/1")

        # Oxigraph
        oxigraph_dir: str = Field(default="./data/oxigraph")

        # APIs
        nvd_api_key: Optional[str] = Field(default=None)
        nvd_api_url: str = Field(default="https://services.nvd.nist.gov/rest/json/cves/2.0")
        euvd_api_url: str = Field(default="https://euvdservices.enisa.europa.eu/api")

        # Application
        app_host: str = Field(default="0.0.0.0")
        app_port: int = Field(default=8000)
        log_level: str = Field(default="INFO")

        # Cache TTLs (seconds)
        cache_ttl_cve: int = Field(default=86400)
        cache_ttl_exploit: int = Field(default=3600)
        cache_ttl_sparql: int = Field(default=300)

        # Performance
        max_concurrent_subscribers: int = Field(default=50)
        sparql_timeout_seconds: int = Field(default=10)
        max_ingestion_batch_size: int = Field(default=100)
else:
    # Fallback simple settings object when pydantic BaseSettings is unavailable
    class Settings:
        def __init__(self) -> None:
            # Database
            self.database_url = "postgresql://postgres:postgres@localhost:5432/wade"
            # Redis
            self.redis_url = "redis://localhost:6379/0"
            # RabbitMQ / Celery
            self.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
            self.celery_broker_url = self.rabbitmq_url
            self.celery_result_backend = "redis://localhost:6379/1"
            # Oxigraph
            self.oxigraph_dir = "./data/oxigraph"
            # APIs
            self.nvd_api_key = None
            self.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            self.euvd_api_url = "https://euvdservices.enisa.europa.eu/api"
            # Application
            self.app_host = "0.0.0.0"
            self.app_port = 8000
            self.log_level = "INFO"
            # Cache TTLs (seconds)
            self.cache_ttl_cve = 86400
            self.cache_ttl_exploit = 3600
            self.cache_ttl_sparql = 300
            # Performance
            self.max_concurrent_subscribers = 50
            self.sparql_timeout_seconds = 10
            self.max_ingestion_batch_size = 100


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_yaml_config(path: str = "config/settings.yaml") -> dict:
    """Load additional configuration from YAML file.

    Args:
        path: Path to YAML configuration file

    Returns:
        Dictionary with configuration data
    """
    config_path = Path(path)
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}
