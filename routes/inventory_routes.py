from flask import Blueprint, jsonify, request
from services.inventory_service import (
    get_inventory_with_products,
    get_inventory_item_detail,
    handle_product_added,
    handle_product_removed,
    seed_demo_data,
)

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.before_app_request
def ensure_seed_data():
    seed_demo_data()


@inventory_bp.get("/")
def list_inventory():
    items = get_inventory_with_products()
    return jsonify(items), 200


@inventory_bp.get("/<int:item_id>")
def get_item(item_id: int):
    detail = get_inventory_item_detail(item_id)
    if detail is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(detail), 200


@inventory_bp.post("/manual-add")
def manual_add():
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
    detail = get_inventory_item_detail(item.id)
    return jsonify(detail), 201


@inventory_bp.post("/manual-remove")
def manual_remove():
    data = request.get_json(force=True)
    item_id = int(data.get("item_id"))
    quantity = float(data.get("quantity", 0))
    item = handle_product_removed(item_id=item_id, quantity=quantity)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    detail = get_inventory_item_detail(item.id)
    return jsonify(detail), 200
