from datetime import datetime, date
from typing import Optional, List, Dict, Any
from models import InventoryItem, Product
from repository import repository


def parse_expiry_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def handle_product_added(
    product_name: str,
    category: str,
    quantity: float,
    unit: str,
    expiry_date_str: Optional[str],
) -> InventoryItem:
    product = repository.get_or_create_product(product_name, category)
    expiry = parse_expiry_date(expiry_date_str)
    item = repository.upsert_inventory_item(
        product_id=product.id,
        quantity_delta=quantity,
        unit=unit,
        expiry_date=expiry,
    )
    repository.create_event(
        "product_added",
        {
            "product_id": product.id,
            "quantity": quantity,
            "unit": unit,
            "expiry_date": expiry.isoformat() if expiry else None,
        },
    )
    return item


def handle_product_removed(item_id: int, quantity: float) -> Optional[InventoryItem]:
    item = repository.adjust_inventory_by_item_id(item_id=item_id, quantity_delta=-quantity)
    if item is None:
        return None
    repository.create_event(
        "product_removed",
        {
            "item_id": item_id,
            "quantity": quantity,
        },
    )
    return item


def get_inventory() -> List[InventoryItem]:
    return repository.list_inventory()


def get_inventory_with_products() -> List[Dict[str, Any]]:
    items = repository.list_inventory()
    result: List[Dict[str, Any]] = []
    for item in items:
        product = repository.get_product(item.product_id)
        result.append(
            {
                "item_id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else None,
                "category": product.category if product else None,
                "quantity": item.quantity,
                "unit": item.unit,
                "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
                "last_updated": item.last_updated.isoformat(),
            }
        )
    return result


def get_inventory_item_detail(item_id: int) -> Optional[Dict[str, Any]]:
    item = repository.get_inventory_item(item_id)
    if item is None:
        return None
    product = repository.get_product(item.product_id)
    return {
        "item_id": item.id,
        "product_id": item.product_id,
        "product_name": product.name if product else None,
        "category": product.category if product else None,
        "quantity": item.quantity,
        "unit": item.unit,
        "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
        "last_updated": item.last_updated.isoformat(),
    }


def seed_demo_data() -> None:
    if repository.list_inventory():
        return
    now = datetime.utcnow().date()
    handle_product_added("Milk 2.5%", "Dairy", 1.0, "pcs", now.isoformat())
    handle_product_added("Eggs", "Dairy", 10, "pcs", None)
    handle_product_added("Tomato", "Vegetables", 500, "g", None)
