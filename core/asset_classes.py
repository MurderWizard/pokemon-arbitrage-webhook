"""
Asset Class Definitions - Core infrastructure for handling different types of collectibles
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from decimal import Decimal
from datetime import datetime

@dataclass
class MarketMetrics:
    """Universal market metrics for any asset"""
    current_price: Decimal
    historic_high: Decimal
    historic_low: Decimal
    avg_30d_price: Decimal
    volume_30d: int
    last_sale_date: datetime
    price_trend_30d: float  # Percentage change
    liquidity_score: float  # 0-1 score based on sales velocity
    market_depth: int       # Number of active listings
    price_volatility: float # Standard deviation of price changes

@dataclass
class GradingInfo:
    """Universal grading information"""
    grading_company: str  # PSA, BGS, CGC, etc.
    grade: str           # Numeric or text grade
    population: int      # Population at this grade
    higher_pop: int     # Population at higher grades
    total_pop: int      # Total graded population
    certification: str   # Cert number if available
    last_grading_cost: Decimal  # Latest known grading cost
    typical_turnaround: int     # Days

class CollectibleAsset(ABC):
    """Base class for all collectible assets"""
    
    def __init__(self):
        self.market_data = None
        self.grading_data = {}  # Data from multiple grading companies
        
    @abstractmethod
    def get_market_price(self, condition: str) -> tuple[Decimal, float]:
        """Get market price and confidence score"""
        pass
        
    @abstractmethod
    def calculate_grading_roi(self, purchase_price: Decimal, condition: str) -> Dict:
        """Calculate ROI for grading this asset"""
        pass
        
    @abstractmethod
    def get_authentication_requirements(self) -> List[str]:
        """Get required authentication steps"""
        pass
        
    @abstractmethod
    def get_storage_requirements(self) -> Dict[str, str]:
        """Get storage/preservation requirements"""
        pass
        
    @abstractmethod
    def get_market_correlation(self) -> float:
        """Get correlation with broader market"""
        pass

class TradingCard(CollectibleAsset):
    """Base class for all trading cards (Pokemon, Sports, MTG, etc)"""
    
    def __init__(self, card_name: str, set_name: str, year: int):
        super().__init__()
        self.card_name = card_name
        self.set_name = set_name
        self.year = year
        self.card_type = None  # Game-specific type
        
    def get_storage_requirements(self) -> Dict[str, str]:
        return {
            "sleeve": "Penny sleeve or better",
            "toploader": "Standard 3x4 35pt",
            "temperature": "65-72°F",
            "humidity": "45-50%",
            "light": "Minimal UV exposure",
            "handling": "Clean, dry hands or gloves"
        }

class Coin(CollectibleAsset):
    """Base class for collectible coins"""
    
    def __init__(self, year: int, mint: str, denomination: str):
        super().__init__()
        self.year = year
        self.mint = mint
        self.denomination = denomination
        self.metal_content = None
        
    def get_storage_requirements(self) -> Dict[str, str]:
        return {
            "holder": "Air-tite or similar",
            "environment": "No PVC exposure",
            "humidity": "30-40%",
            "handling": "Cotton gloves only",
            "cleaning": "Never clean rare coins"
        }

class Comic(CollectibleAsset):
    """Base class for comic books"""
    
    def __init__(self, title: str, issue: int, publisher: str, year: int):
        super().__init__()
        self.title = title
        self.issue = issue
        self.publisher = publisher
        self.year = year
        
    def get_storage_requirements(self) -> Dict[str, str]:
        return {
            "bag": "Mylar with acid-free board",
            "temperature": "65-70°F",
            "humidity": "50%",
            "position": "Vertical storage",
            "light": "Zero UV exposure"
        }

class Sneaker(CollectibleAsset):
    """Base class for collectible sneakers"""
    
    def __init__(self, brand: str, model: str, size: str, year: int):
        super().__init__()
        self.brand = brand
        self.model = model
        self.size = size
        self.year = year
        
    def get_storage_requirements(self) -> Dict[str, str]:
        return {
            "box": "Original box required",
            "temperature": "60-80°F",
            "humidity": "40-50%",
            "position": "Flat storage",
            "cleaning": "No cleaning products"
        }

class Watch(CollectibleAsset):
    """Base class for collectible watches"""
    
    def __init__(self, brand: str, model: str, reference: str, year: int):
        super().__init__()
        self.brand = brand
        self.model = model
        self.reference = reference
        self.year = year
        self.movement = None
        
    def get_storage_requirements(self) -> Dict[str, str]:
        return {
            "box": "Original box and papers",
            "winder": "If automatic movement",
            "service": "Every 3-5 years",
            "water": "Check seals annually",
            "magnetism": "Keep away from magnets"
        }
