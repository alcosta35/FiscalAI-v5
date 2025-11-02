# config.py
"""
Configuration settings for FiscalAI
"""
from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Determine if running in Colab
IS_COLAB = 'COLAB_GPU' in os.environ

# Data directory - different for Colab vs local
if IS_COLAB:
    DATA_DIR = Path('/content/data')
else:
    DATA_DIR = Path(__file__).parent / 'data'


class Settings(BaseSettings):
    """Application settings"""
    
    # App info
    app_name: str = "FiscalAI - Auditor Fiscal Inteligente"
    app_version: str = "2.0.0"

    # API settings
    api_prefix: str = "/api"
        
    # OpenAI API
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Pinecone settings
    pinecone_api_key: str = ""
    pinecone_index_name: str = "cfop-fiscal"
    pinecone_namespace: str = "default"
    pinecone_host: str = "https://cfop-fiscal-x8q6et6.svc.aped-4627-b74a.pinecone.io"
    pinecone_dimension: int = 1536
    pinecone_metric: str = "cosine"
    
    # Ngrok settings
    ngrok_auth_token: str = ""

    # CORS settings
    cors_origins: list = ["*"]
    
    # CSV file paths
    cabecalho_csv: str = str(DATA_DIR / "202401_NFs_Cabecalho.csv")
    itens_csv: str = str(DATA_DIR / "202401_NFs_Itens.csv")
    cfop_csv: str = str(DATA_DIR / "CFOP.csv")
    
    # Estatísticas
    MAX_SAMPLE_SIZE: int = 200
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
