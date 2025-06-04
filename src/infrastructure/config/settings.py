from functools import lru_cache
from typing import Optional, Dict, Any

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Restaurant Order Service"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for managing restaurant orders"
    DEBUG: bool = False
    
    # Database settings
    ORDER_DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_ORDER_TOPIC: str = "restaurant.orders"
    KAFKA_CLIENT_ID: str = "order-service"
    KAFKA_GROUP_ID: str = "order-service-group"
    
    # Inventory service settings
    INVENTORY_SERVICE_URL: str
    INVENTORY_SERVICE_TIMEOUT: int = 5  # seconds
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    @field_validator("CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str) -> list:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()