from datetime import date
from fastapi.testclient import TestClient
from backend.main import app

# ------------------ get all users tests -------------- #
# Since we know it will always be sorted by id, I didn't execute any other sorting tests #
def test_get_all_users():
    client = TestClient(app)
    response = client.get("/users")
    assert response.status_code == 200

    meta = response.json()["meta"]
    users = response.json()["users"]
    assert meta["count"] == len(users)
    assert users == sorted(users, key=lambda user: user["id"])

#  ------------ create user tests --------------- #
def test_create_user():
    client = TestClient(app)
    response = client.post(
        "/users",
        json={
            "id": "banana"
        },
    )
    assert response.status_code == 200
    assert response.json()["user"]["id"] == "banana"

def test_create_user_check_data():
    create_params = {
        "id": "soup",
    }

    client = TestClient(app)
    response = client.post("/users", json=create_params)
    assert response.status_code == 200

    data = response.json()
    assert "user" in data
    user = data["user"]
    for key, value in create_params.items():
        assert user[key] == value

    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    user = data["user"]
    for key, value in create_params.items():
        assert user[key] == value

def test_create_invalid_user():
    create_params = {
        "id": "ripley"
    }
    client = TestClient(app)
    response = client.post("/users", json=create_params)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "type": "duplicate_entity",
            "entity_name": "User",
            "entity_id": "ripley"
        }
    }

#  ------- get user by id tests -------------- #
def test_get_user():
    user_id = "bishop"
    expected_user = {
        "id": user_id, 
        "created_at": "2014-04-14T10:49:07"
    }

    client = TestClient(app)
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"user": expected_user}

def test_get_invalid_user():
    user_id = "123"
    client = TestClient(app)
    response = client.get(f"/users/{user_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "User",
            "entity_id": user_id
        }
    }

# ------------- get user chats by user id tests ----------------- #
def test_get_chats_by_id():
    user_id = "bomb20"
    client = TestClient(app)
    response = client.get(f"/users/{user_id}/chats")

    assert response.status_code == 200
    data = response.json()

    assert "meta" in data
    assert "chats" in data
    assert "count" in data["meta"]
    assert isinstance(data["meta"]["count"], int)

def test_get_chats_invalid_id():
    user_id = "riley"
    client = TestClient(app)
    response = client.get(f"/users/{user_id}/chats")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
                "type": "entity_not_found",
                "entity_name": "User",
                "entity_id": user_id
        }
    }