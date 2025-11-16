def test_manual_add_and_get_item(client):
    payload = {
        "product_name": "Test Milk",
        "category": "Dairy",
        "quantity": 1,
        "unit": "pcs",
        "expiry_date": None,
    }
    resp = client.post("/api/inventory/manual-add", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["product_name"] == "Test Milk"
    item_id = data["item_id"]

    resp_get = client.get(f"/api/inventory/{item_id}")
    assert resp_get.status_code == 200
    data_get = resp_get.get_json()
    assert data_get["item_id"] == item_id
    assert data_get["product_name"] == "Test Milk"


def test_manual_remove_not_found(client):
    resp = client.post(
        "/api/inventory/manual-remove",
        json={"item_id": 99999, "quantity": 1},
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_stats_summary_reflects_inventory(client):
    client.post(
        "/api/inventory/manual-add",
        json={
            "product_name": "Cheese",
            "category": "Dairy",
            "quantity": 2,
            "unit": "pcs",
            "expiry_date": None,
        },
    )
    client.post(
        "/api/inventory/manual-add",
        json={
            "product_name": "Tomato",
            "category": "Vegetables",
            "quantity": 500,
            "unit": "g",
            "expiry_date": None,
        },
    )

    resp_stats = client.get("/api/stats/summary")
    assert resp_stats.status_code == 200
    stats = resp_stats.get_json()
    assert stats["total_items"] >= 2
    assert "total_quantity" in stats
    assert isinstance(stats["top_categories"], list)
    categories = {c["category"] for c in stats["top_categories"]}
    assert "Dairy" in categories or "Vegetables" in categories
