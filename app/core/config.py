import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DB_URL: str = os.getenv("DB_URL", "postgresql://flip:secure_password@localhost:5433/pokemon_arbitrage")
    
    # Telegram
    TG_TOKEN: Optional[str] = os.getenv("TG_TOKEN")
    TG_ADMIN_ID: Optional[str] = os.getenv("TG_ADMIN_ID")
    
    # TCGplayer
    TCG_CLIENT_ID: Optional[str] = os.getenv("TCG_CLIENT_ID")
    TCG_CLIENT_SECRET: Optional[str] = os.getenv("TCG_CLIENT_SECRET")
    TCG_ACCESS_TOKEN: Optional[str] = os.getenv("TCG_ACCESS_TOKEN")
    
    # eBay
    EBAY_APP_ID: Optional[str] = os.getenv("EBAY_APP_ID")
    EBAY_CERT_ID: Optional[str] = os.getenv("EBAY_CERT_ID")
    EBAY_DEV_ID: Optional[str] = os.getenv("EBAY_DEV_ID")
    EBAY_USER_TOKEN: Optional[str] = os.getenv("EBAY_USER_TOKEN")
    EBAY_ENVIRONMENT: str = os.getenv("EBAY_ENVIRONMENT", "sandbox")
    
    # eBay Webhook
    EBAY_WEBHOOK_URL: Optional[str] = os.getenv("EBAY_WEBHOOK_URL")
    EBAY_VERIFICATION_TOKEN: Optional[str] = os.getenv("EBAY_VERIFICATION_TOKEN")
    
    class ModelConfig:
        env_file = '.env'
        env_file_encoding = 'utf-8'
    
    # COMC
    COMC_USERNAME: Optional[str] = os.getenv("COMC_USERNAME")
    COMC_PASSWORD: Optional[str] = os.getenv("COMC_PASSWORD")
    COMC_MAILBOX_ADDRESS: Optional[str] = os.getenv("COMC_MAILBOX_ADDRESS")
    
    # PSA Vault
    PSA_VAULT_USERNAME: Optional[str] = os.getenv("PSA_VAULT_USERNAME")
    PSA_VAULT_PASSWORD: Optional[str] = os.getenv("PSA_VAULT_PASSWORD")
    
    # PriceCharting
    PRICECHARTING_API_KEY: Optional[str] = os.getenv("PRICECHARTING_API_KEY")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6380")
    
    # Trading Parameters
    STARTING_BANKROLL: float = float(os.getenv("STARTING_BANKROLL", 1000.0))
    MAX_POSITION_PERCENT: float = float(os.getenv("MAX_POSITION_PERCENT", 5.0))
    DEAL_THRESHOLD: float = float(os.getenv("DEAL_THRESHOLD", 0.75))
    MIN_PROFIT_MARGIN: float = float(os.getenv("MIN_PROFIT_MARGIN", 0.25))
    RAW_AGING_DAYS: int = int(os.getenv("RAW_AGING_DAYS", 45))
    SLAB_AGING_DAYS: int = int(os.getenv("SLAB_AGING_DAYS", 30))
    
    # Risk Controls
    ENABLE_AUTO_BUY: bool = os.getenv("ENABLE_AUTO_BUY", "False").lower() == "true"
    DAILY_SPEND_LIMIT: float = float(os.getenv("DAILY_SPEND_LIMIT", 200.0))
    STOP_LOSS_THRESHOLD: float = float(os.getenv("STOP_LOSS_THRESHOLD", 0.6))
    
    # Enhanced Auto-Buy Settings
    AUTO_BUY_ENABLED: bool = os.getenv("AUTO_BUY_ENABLED", "False").lower() == "true"
    MAX_AUTO_BUY_AMOUNT: float = float(os.getenv("MAX_AUTO_BUY_AMOUNT", 200.0))
    DAILY_AUTO_BUY_LIMIT: float = float(os.getenv("DAILY_AUTO_BUY_LIMIT", 500.0))
    MIN_AUTO_BUY_MARGIN: float = float(os.getenv("MIN_AUTO_BUY_MARGIN", 0.35))
    AUTO_BUY_CONFIDENCE_THRESHOLD: float = float(os.getenv("AUTO_BUY_CONFIDENCE_THRESHOLD", 0.8))
    
    # Discord Integration
    DISCORD_BOT_TOKEN: Optional[str] = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_DEAL_CHANNELS: Optional[str] = os.getenv("DISCORD_DEAL_CHANNELS")
    
    # Compliance
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "Pokemon Card Arbitrage")
    SALES_TAX_RATE: float = float(os.getenv("SALES_TAX_RATE", 0.08))
    TAX_YEAR: int = int(os.getenv("TAX_YEAR", 2025))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()
