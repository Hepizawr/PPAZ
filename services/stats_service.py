from collections import Counter
from datetime import date
from typing import Dict, Any
from repository import repository


def get_summary_stats() -> Dict[str, Any]:
    inventory = repository.list_inventory()
    products = repository.list_products()
    product_by_id = {p.id: p for p in products}

    total_items = len(inventory)
    total_quantity = sum(item.quantity for item in inventory)

    category_counter = Counter()
    for item in inventory:
        product = product_by_id.get(item.product_id)
        if product is None:
            continue
        category_counter[product.category] += item.quantity

    today = date.today()
    expiring_soon = []
    for item in inventory:
        if item.expiry_date and (item.expiry_date - today).days <= 3:
            product = product_by_id.get(item.product_id)
            expiring_soon.append(
                {
                    "item_id": item.id,
                    "product_name": product.name if product else None,
                    "category": product.category if product else None,
                    "expiry_date": item.expiry_date.isoformat(),
                }
            )

    top_categories = [
        {"category": name, "total_quantity": qty}
        for name, qty in category_counter.most_common(3)
    ]

    return {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "top_categories": top_categories,
        "expiring_soon": expiring_soon,
    }
