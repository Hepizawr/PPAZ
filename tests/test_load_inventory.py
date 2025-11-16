import time
import random


def test_load_product_added_and_inventory_listing(client):
    iterations = 200
    start = time.perf_counter()

    for i in range(iterations):
        name = f"TestProduct{i % 5}"
        category = "LoadTest"
        quantity = random.uniform(0.1, 2.0)
        unit = "pcs"
        payload = {
            "product_name": name,
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "expiry_date": None,
        }
        resp = client.post("/api/events/product-added", json=payload)
        assert resp.status_code == 201

        if i % 10 == 0:
            resp_list = client.get("/api/inventory/")
            assert resp_list.status_code == 200
            data = resp_list.get_json()
            assert isinstance(data, list)

    duration = time.perf_counter() - start
    assert duration < 5.0


def test_load_stats_summary_under_load(client):
    for i in range(100):
        name = f"Milk{i % 3}"
        category = "Dairy"
        payload = {
            "product_name": name,
            "category": category,
            "quantity": 1,
            "unit": "pcs",
            "expiry_date": None,
        }
        resp = client.post("/api/events/product-added", json=payload)
        assert resp.status_code == 201

    start = time.perf_counter()
    for _ in range(50):
        resp_stats = client.get("/api/stats/summary")
        assert resp_stats.status_code == 200
        data = resp_stats.get_json()
        assert "total_items" in data
        assert "total_quantity" in data
        assert "top_categories" in data
    duration = time.perf_counter() - start
    assert duration < 3.0
