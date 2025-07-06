from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CardType(str, Enum):
    RAW = "raw"
    GRADED = "graded"

class InventoryStatus(str, Enum):
    PURCHASED = "purchased"
    IN_TRANSIT = "in_transit"
    PROCESSING = "processing"
    LISTED = "listed"
    SOLD = "sold"
    AGED = "aged"

class Platform(str, Enum):
    EBAY = "ebay"
    COMC = "comc"
    TCGPLAYER = "tcgplayer"
    PSA_VAULT = "psa_vault"

# Card schemas
class CardBase(BaseModel):
    name: str
    set_name: str
    number: Optional[str] = None
    rarity: Optional[str] = None
    condition: str = "NM"
    card_type: CardType
    grade: Optional[int] = None
    tcg_product_id: Optional[str] = None

class CardCreate(CardBase):
    pass

class Card(CardBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Inventory schemas
class InventoryItemBase(BaseModel):
    card_id: int
    sku: str
    purchase_price: float
    purchase_date: datetime
    purchase_platform: str
    current_price: Optional[float] = None
    list_price: Optional[float] = None
    status: InventoryStatus = InventoryStatus.PURCHASED
    platform: Optional[str] = None
    days_in_stock: int = 0

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItem(InventoryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    card: Card
    
    class Config:
        from_attributes = True

# Deal schemas
class DealBase(BaseModel):
    card_name: str
    set_name: str
    condition: str
    listing_price: float
    market_price: float
    profit_margin: float
    platform: str
    listing_url: str
    status: str = "found"

class DealCreate(DealBase):
    pass

class Deal(DealBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Sale schemas
class SaleBase(BaseModel):
    inventory_item_id: int
    sale_price: float
    sale_date: datetime
    platform: str
    fees: float = 0.0
    net_profit: float

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Price history schemas
class PriceHistoryBase(BaseModel):
    card_id: int
    platform: str
    price_type: str
    price: float
    date: datetime

class PriceHistoryCreate(PriceHistoryBase):
    pass

class PriceHistory(PriceHistoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    type: str
    amount: float
    description: str
    platform: Optional[str] = None
    reference_id: Optional[str] = None
    date: datetime

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analytics schemas
class ProfitSummary(BaseModel):
    total_revenue: float
    total_costs: float
    net_profit: float
    profit_margin: float
    roi: float

class AgedInventoryItem(BaseModel):
    id: int
    sku: str
    card_name: str
    purchase_price: float
    current_price: Optional[float]
    days_in_stock: int
    status: str
