from datetime import datetime, date
from typing import Dict, List, Optional
from models import Product, InventoryItem, Event


class InMemoryRepository:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.inventory: Dict[int, InventoryItem] = {}
        self.events: Dict[int, Event] = {}
        self._product_seq = 1
        self._inventory_seq = 1
        self._event_seq = 1

    def get_or_create_product(self, name: str, category: str) -> Product:
        for product in self.products.values():
            if product.name == name and product.category == category:
                return product
        product = Product(id=self._product_seq, name=name, category=category)
        self.products[self._product_seq] = product
        self._product_seq += 1
        return product

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)

    def list_products(self) -> List[Product]:
        return list(self.products.values())

    def upsert_inventory_item(
        self,
        product_id: int,
        quantity_delta: float,
        unit: str,
        expiry_date: Optional[date],
    ) -> InventoryItem:
        existing = None
        for item in self.inventory.values():
            if item.product_id == product_id and item.unit == unit:
                existing = item
                break
        now = datetime.utcnow()
        if existing is None:
            item = InventoryItem(
                id=self._inventory_seq,
                product_id=product_id,
                quantity=max(quantity_delta, 0.0),
                unit=unit,
                expiry_date=expiry_date,
                last_updated=now,
            )
            self.inventory[self._inventory_seq] = item
            self._inventory_seq += 1
            return item
        new_quantity = existing.quantity + quantity_delta
        existing.quantity = max(new_quantity, 0.0)
        if expiry_date is not None:
            existing.expiry_date = expiry_date
        existing.last_updated = now
        return existing

    def adjust_inventory_by_item_id(
        self, item_id: int, quantity_delta: float
    ) -> Optional[InventoryItem]:
        item = self.inventory.get(item_id)
        if item is None:
            return None
        now = datetime.utcnow()
        new_quantity = item.quantity + quantity_delta
        item.quantity = max(new_quantity, 0.0)
        item.last_updated = now
        return item

    def list_inventory(self) -> List[InventoryItem]:
        return list(self.inventory.values())

    def get_inventory_item(self, item_id: int) -> Optional[InventoryItem]:
        return self.inventory.get(item_id)

    def create_event(self, type_: str, payload: dict) -> Event:
        event = Event(
            id=self._event_seq,
            type=type_,
            payload=payload,
            created_at=datetime.utcnow(),
        )
        self.events[self._event_seq] = event
        self._event_seq += 1
        return event

    def list_events(self) -> List[Event]:
        return list(self.events.values())


repository = InMemoryRepository()
