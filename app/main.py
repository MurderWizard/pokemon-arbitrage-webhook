from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging

from app.database import SessionLocal, engine, Base
from app.api.routes import inventory, deals, pricing, analytics
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Pokemon Card Arbitrage API")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down Pokemon Card Arbitrage API")

app = FastAPI(
    title="Pokemon Card Arbitrage API",
    description="Automated trading system for Pokemon cards",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(deals.router, prefix="/api/v1/deals", tags=["deals"])
app.include_router(pricing.router, prefix="/api/v1/pricing", tags=["pricing"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Pokemon Card Arbitrage API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "bankroll": settings.STARTING_BANKROLL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
