import pytest
from tests.conftest import get_token

class TestTables:
    def test_list_tables(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.get("/api/tables/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_create_table_admin(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.post("/api/tables/", json={"code": "T99", "area": "VIP", "capacity": 2},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 201
        assert r.json()["code"] == "T99"

    def test_create_table_duplicate_code(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.post("/api/tables/", json={"code": "M01", "area": "A", "capacity": 4},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400

    def test_create_table_invalid_capacity(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.post("/api/tables/", json={"code": "T00", "area": "A", "capacity": 0},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 422

    def test_update_table_status(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        table_id = seed_data["table"].table_id
        r = client.put(f"/api/tables/{table_id}", json={"status": "OCUPADA"},
                       headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["status"] == "OCUPADA"

    def test_delete_table_no_orders(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.post("/api/tables/", json={"code": "DEL1", "area": "A", "capacity": 2},
                        headers={"Authorization": f"Bearer {token}"})
        table_id = r.json()["table_id"]
        r2 = client.delete(f"/api/tables/{table_id}", headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 204

class TestMenu:
    def test_list_categories(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.get("/api/menu/categories", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200

    def test_create_category(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.post("/api/menu/categories", json={"name": "Bebidas"},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 201

    def test_list_items(self, client, seed_data):
        token = get_token(client, "mesero1", "mes123")
        r = client.get("/api/menu/items", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_create_item(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        cat_id = seed_data["item"].category_id
        r = client.post("/api/menu/items", json={"category_id": cat_id, "name": "Nuevo plato", "price": 55.00},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 201
        assert r.json()["name"] == "Nuevo plato"

    def test_create_item_negative_price(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        cat_id = seed_data["item"].category_id
        r = client.post("/api/menu/items", json={"category_id": cat_id, "name": "X", "price": -5},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 422

    def test_mark_item_out_of_stock(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        item_id = seed_data["item"].item_id
        r = client.put(f"/api/menu/items/{item_id}", json={"out_of_stock": True},
                       headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["out_of_stock"] is True

class TestOrders:
    def _mesero_token(self, client, seed_data):
        return get_token(client, "mesero1", "mes123")

    def test_create_order(self, client, seed_data):
        token = self._mesero_token(client, seed_data)
        table_id = seed_data["table"].table_id
        r = client.post("/api/orders/", json={"table_id": table_id},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 201
        assert r.json()["status"] == "ABIERTO"

    def test_create_duplicate_order_same_table(self, client, seed_data):
        token = self._mesero_token(client, seed_data)
        table_id = seed_data["table"].table_id
        client.post("/api/orders/", json={"table_id": table_id},
                    headers={"Authorization": f"Bearer {token}"})
        r2 = client.post("/api/orders/", json={"table_id": table_id},
                         headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 400

    def test_add_item_to_order(self, client, seed_data):
        token = self._mesero_token(client, seed_data)
        table_id = seed_data["table"].table_id
        order = client.post("/api/orders/", json={"table_id": table_id},
                            headers={"Authorization": f"Bearer {token}"}).json()
        item_id = seed_data["item"].item_id
        r = client.post(f"/api/orders/{order['order_id']}/items",
                        json={"item_id": item_id, "quantity": 2, "notes": "sin sal"},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert len(r.json()["items"]) == 1

    def test_send_to_kitchen(self, client, seed_data):
        token = self._mesero_token(client, seed_data)
        table_id = seed_data["table"].table_id
        order = client.post("/api/orders/", json={"table_id": table_id},
                            headers={"Authorization": f"Bearer {token}"}).json()
        item_id = seed_data["item"].item_id
        client.post(f"/api/orders/{order['order_id']}/items",
                    json={"item_id": item_id, "quantity": 1},
                    headers={"Authorization": f"Bearer {token}"})
        r = client.post(f"/api/orders/{order['order_id']}/send-to-kitchen",
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["status"] == "ENVIADO"

    def test_send_empty_order_fails(self, client, seed_data):
        token = self._mesero_token(client, seed_data)
        table_id = seed_data["table"].table_id
        order = client.post("/api/orders/", json={"table_id": table_id},
                            headers={"Authorization": f"Bearer {token}"}).json()
        r = client.post(f"/api/orders/{order['order_id']}/send-to-kitchen",
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400

    def test_kitchen_status_flow(self, client, seed_data):
        token_m = self._mesero_token(client, seed_data)
        token_c = get_token(client, "cocina1", "coc123")
        table_id = seed_data["table"].table_id
        order = client.post("/api/orders/", json={"table_id": table_id},
                            headers={"Authorization": f"Bearer {token_m}"}).json()
        item_id = seed_data["item"].item_id
        client.post(f"/api/orders/{order['order_id']}/items",
                    json={"item_id": item_id, "quantity": 1},
                    headers={"Authorization": f"Bearer {token_m}"})
        client.post(f"/api/orders/{order['order_id']}/send-to-kitchen",
                    headers={"Authorization": f"Bearer {token_m}"})
        r = client.post(f"/api/orders/{order['order_id']}/kitchen-status",
                        params={"new_status": "EN_PREPARACION"},
                        headers={"Authorization": f"Bearer {token_c}"})
        assert r.status_code == 200
        assert r.json()["status"] == "EN_PREPARACION"

class TestBilling:
    def test_generate_and_pay_bill(self, client, seed_data):
        token_m = get_token(client, "mesero1", "mes123")
        token_caj = get_token(client, "cajero1", "caj123")
        table_id = seed_data["table"].table_id
        order = client.post("/api/orders/", json={"table_id": table_id},
                            headers={"Authorization": f"Bearer {token_m}"}).json()
        item_id = seed_data["item"].item_id
        client.post(f"/api/orders/{order['order_id']}/items",
                    json={"item_id": item_id, "quantity": 2},
                    headers={"Authorization": f"Bearer {token_m}"})
        r_bill = client.post(f"/api/billing/orders/{order['order_id']}/bill",
                             headers={"Authorization": f"Bearer {token_caj}"})
        assert r_bill.status_code == 200
        bill = r_bill.json()
        assert float(bill["total"]) == 200.00
        r_pay = client.post(f"/api/billing/orders/{order['order_id']}/pay",
                            json={"amount": 200.00},
                            headers={"Authorization": f"Bearer {token_caj}"})
        assert r_pay.status_code == 200
        assert r_pay.json()["paid"] is True

    def test_pay_insufficient_amount(self, client, seed_data):
        token_m = get_token(client, "mesero1", "mes123")
        token_caj = get_token(client, "cajero1", "caj123")
        table_id = seed_data["table"].table_id
        order = client.post("/api/orders/", json={"table_id": table_id},
                            headers={"Authorization": f"Bearer {token_m}"}).json()
        item_id = seed_data["item"].item_id
        client.post(f"/api/orders/{order['order_id']}/items",
                    json={"item_id": item_id, "quantity": 1},
                    headers={"Authorization": f"Bearer {token_m}"})
        client.post(f"/api/billing/orders/{order['order_id']}/bill",
                    headers={"Authorization": f"Bearer {token_caj}"})
        r = client.post(f"/api/billing/orders/{order['order_id']}/pay",
                        json={"amount": 10.00},
                        headers={"Authorization": f"Bearer {token_caj}"})
        assert r.status_code == 400
