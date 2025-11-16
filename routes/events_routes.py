from flask import Blueprint, jsonify, request
from services.inventory_service import handle_product_added, handle_product_removed

events_bp = Blueprint("events", __name__)


@events_bp.post("/product-added")
def product_added():
    data = request.get_json(force=True)
    name = data.get("product_name")
    category = data.get("category", "General")
    quantity = float(data.get("quantity", 0))
    unit = data.get("unit", "pcs")
    expiry_date = data.get("expiry_date")
    item = handle_product_added(
        product_name=name,
        category=category,
        quantity=quantity,
        unit=unit,
        expiry_date_str=expiry_date,
    )
    return jsonify({"item_id": item.id}), 201


@events_bp.post("/product-removed")
def product_removed():
    data = request.get_json(force=True)
    item_id = int(data.get("item_id"))
    quantity = float(data.get("quantity", 0))
    item = handle_product_removed(item_id=item_id, quantity=quantity)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"item_id": item.id, "remaining_quantity": item.quantity}), 200
