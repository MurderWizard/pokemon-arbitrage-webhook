from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class CardType(enum.Enum):
    RAW = "raw"
    GRADED = "graded"

class InventoryStatus(enum.Enum):
    PURCHASED = "purchased"
    IN_TRANSIT = "in_transit"
    PROCESSING = "processing"
    LISTED = "listed"
    SOLD = "sold"
    AGED = "aged"

class Platform(enum.Enum):
    EBAY = "ebay"
    COMC = "comc"
    TCGPLAYER = "tcgplayer"
    PSA_VAULT = "psa_vault"

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    set_name = Column(String, nullable=False)
    number = Column(String, nullable=True)
    rarity = Column(String, nullable=True)
    condition = Column(String, nullable=False, default="NM")
    card_type = Column(String, nullable=False)  # raw or graded
    grade = Column(Integer, nullable=True)  # PSA grade if applicable
    tcg_product_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="card")
    price_history = relationship("PriceHistory", back_populates="card")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    sku = Column(String, unique=True, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    purchase_platform = Column(String, nullable=False)
    current_price = Column(Float, nullable=True)
    list_price = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="purchased")
    platform = Column(String, nullable=True)  # Where it's currently listed
    days_in_stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    card = relationship("Card", back_populates="inventory_items")
    sales = relationship("Sale", back_populates="inventory_item")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    platform = Column(String, nullable=False)
    price_type = Column(String, nullable=False)  # market, median, low, high
    price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    card = relationship("Card", back_populates="price_history")

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    card_name = Column(String, nullable=False)
    set_name = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    listing_price = Column(Float, nullable=False)
    market_price = Column(Float, nullable=False)
    profit_margin = Column(Float, nullable=False)
    platform = Column(String, nullable=False)
    listing_url = Column(String, nullable=False)
    status = Column(String, nullable=False, default="found")  # found, purchased, passed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    platform = Column(String, nullable=False)
    fees = Column(Float, nullable=False, default=0.0)
    net_profit = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="sales")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # purchase, sale, fee, tax
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    platform = Column(String, nullable=True)
    reference_id = Column(String, nullable=True)  # External transaction ID
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
