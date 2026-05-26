import pytest
from tests.conftest import get_token

class TestAuth:
    def test_login_success(self, client, seed_data):
        r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["role"] == "ADMIN"

    def test_login_wrong_password(self, client, seed_data):
        r = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert r.status_code == 401

    def test_login_inactive_user(self, client, seed_data, db):
        seed_data["mesero"].active = False
        db.commit()
        r = client.post("/api/auth/login", json={"username": "mesero1", "password": "mes123"})
        assert r.status_code == 401

    def test_get_me(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["username"] == "admin"

    def test_me_no_token(self, client, seed_data):
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_me_invalid_token(self, client, seed_data):
        r = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert r.status_code == 401

class TestUsers:
    def test_list_users_admin(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_list_users_forbidden_for_mesero(self, client, seed_data):
        token = get_token(client, "mesero1", "mes123")
        r = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403

    def test_create_user(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        r = client.post("/api/users/", json={"username": "nuevo", "password": "pass123",
                                              "full_name": "Nuevo Usuario", "role": "MESERO"},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 201
        assert r.json()["username"] == "nuevo"

    def test_create_duplicate_user(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        payload = {"username": "admin", "password": "x", "full_name": "X", "role": "MESERO"}
        r = client.post("/api/users/", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400

    def test_deactivate_user(self, client, seed_data):
        token = get_token(client, "admin", "admin123")
        user_id = seed_data["mesero"].user_id
        r = client.delete(f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 204
