from typing import Any

from pydantic import computed_field
from pydantic_settings import BaseSettings


class SearchSettings(BaseSettings):
    """Settings for an Azure Search service."""

    search_service_name: str
    api_key: str

    @computed_field
    @property
    def search_service_url(self) -> str:
        """Return the full base URL with API version built in."""
        return f"https://{self.search_service_name}.search.windows.net"

    @computed_field
    @property
    def search_service_headers(self) -> dict:
        """Return the headers needed for authentication."""
        return {"api-key": self.api_key, "Content-Type": "application/json"}


class Settings(BaseSettings):
    """Top-level settings containing all sub-settings."""

    api_version: str
    allow_index_downtime: bool = True
    old_search: SearchSettings
    new_search: SearchSettings
    batch_size: int = 1000
    
    @computed_field
    @property
    def list_params(self) -> dict[str, Any]:
        return {"api-version": self.api_version}

    @computed_field
    @property
    def create_params(self) -> dict[str, Any]:
        return {
            "api-version": self.api_version,
            "allowIndexDowntime": str(self.allow_index_downtime),
        }

    @computed_field
    @property
    def search_params(self) -> dict[str, Any]:
        return {
            "api-version": self.api_version,
            "allowIndexDowntime": str(self.allow_index_downtime),
        }

    @computed_field
    @property
    def upload_params(self) -> dict[str, Any]:
        return {"api-version": self.api_version}


settings = Settings()
