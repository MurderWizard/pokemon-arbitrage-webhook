from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DB_URL: str = "postgresql://flip:secure_password@localhost:5433/pokemon_arbitrage"
    
    # Telegram
    TG_TOKEN: str = ""
    TG_ADMIN_ID: str = ""
    
    # TCGplayer
    TCG_CLIENT_ID: str = ""
    TCG_CLIENT_SECRET: str = ""
    TCG_ACCESS_TOKEN: str = ""
    
    # eBay
    EBAY_APP_ID: str = ""
    EBAY_CERT_ID: str = ""
    EBAY_USER_TOKEN: str = ""
    EBAY_ENVIRONMENT: str = "sandbox"
    
    # COMC
    COMC_USERNAME: str = ""
    COMC_PASSWORD: str = ""
    COMC_MAILBOX_ADDRESS: str = ""
    
    # PSA Vault
    PSA_VAULT_USERNAME: str = ""
    PSA_VAULT_PASSWORD: str = ""
    
    # PriceCharting
    PRICECHARTING_API_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6380"
    
    # Trading Parameters
    STARTING_BANKROLL: float = 1000.0
    MAX_POSITION_PERCENT: float = 5.0
    DEAL_THRESHOLD: float = 0.75
    MIN_PROFIT_MARGIN: float = 0.25
    RAW_AGING_DAYS: int = 45
    SLAB_AGING_DAYS: int = 30
    
    # Risk Controls
    ENABLE_AUTO_BUY: bool = False
    DAILY_SPEND_LIMIT: float = 200.0
    STOP_LOSS_THRESHOLD: float = 0.6
    
    # Enhanced Auto-Buy Settings
    AUTO_BUY_ENABLED: bool = False
    MAX_AUTO_BUY_AMOUNT: float = 200.0
    DAILY_AUTO_BUY_LIMIT: float = 500.0
    MIN_AUTO_BUY_MARGIN: float = 0.35
    AUTO_BUY_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Discord Integration
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_DEAL_CHANNELS: str = ""  # Comma-separated channel IDs
    
    # Compliance
    BUSINESS_NAME: str = "Pokemon Card Arbitrage"
    SALES_TAX_RATE: float = 0.08
    TAX_YEAR: int = 2025
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
