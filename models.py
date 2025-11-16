from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any


@dataclass
class Product:
    id: int
    name: str
    category: str


@dataclass
class InventoryItem:
    id: int
    product_id: int
    quantity: float
    unit: str
    expiry_date: Optional[date]
    last_updated: datetime


@dataclass
class Event:
    id: int
    type: str
    payload: Dict[str, Any]
    created_at: datetime
