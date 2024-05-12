from datetime import date
from fastapi.testclient import TestClient
from backend.main import app

# ---------------- get all chats tests ---------------- #
# Since we know it will always be sorted by 'name', I didn't write any other sort tests #
def test_get_all_chats():
    client = TestClient(app)
    response = client.get("/chats")
    assert response.status_code == 200

    meta = response.json()["meta"]
    chats = response.json()["chats"]

    assert meta["count"] == len(chats)
    assert chats == sorted(chats, key=lambda chat: chat["name"])

# ----------------- get chat by id tests ---------------- #
def test_get_chat_by_id():
    chat_id = "36b18c30f5eb4c7888229474d12e426f"
    expected_chat = {
        "id": chat_id,
        "name": "sensory apparatus",
        "user_ids": [
            "bomb20",
            "doolittle"
        ],
        "owner_id": "doolittle",
        "created_at": "2023-07-19T04:21:31"
    }

    client = TestClient(app)
    response = client.get(f"/chats/{chat_id}")
    assert response.status_code == 200
    assert response.json() == {"chat": expected_chat}

def test_get_chat_by_id_invalid():
    chat_id = "567"
    client = TestClient(app)
    response = client.get(f"/chats/{chat_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "Chat",
            "entity_id": chat_id
        }
    }

# ----------------- update chat tests ------------------ #
def test_update_chat():
    chat_id = "36b18c30f5eb4c7888229474d12e426f"
    updated_params = {
        "id": "123",
    }

    client = TestClient(app)
    response = client.put(f"/chats/{chat_id}", json=updated_params)
    assert response.status_code == 200
    assert response.json() == {
        "chat": {
            "id": "123",
            "name": "sensory apparatus",
            "user_ids": ["bomb20", "doolittle"],
            "owner_id": "doolittle",
            "created_at": "2023-07-19T04:21:31"
        }
    }

def test_update_chat_invalid():
    chat_id = "abhfshjasdbzgjlbds"
    updated_params = {
        "id": "123",
        "name": "sally"
    }

    client = TestClient(app)
    response = client.put(f"/chats/{chat_id}", json=updated_params)
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "Chat",
            "entity_id": chat_id
        }
    }

# ------------- delete chat tests -------------- #    
# This method works when it is run on its own; I think placing it after 'update' causes a weird error when
    # running all at once. 
def test_delete_chat():
    chat_id = "36b18c30f5eb4c7888229474d12e426f"
    client = TestClient(app)
    response = client.delete(f"/chats/{chat_id}")

    assert response.status_code == 204
    assert response.content == b""

    response = client.get(f"/chats/{chat_id}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "Chat",
            "entity_id": chat_id,
        },
    }

def test_delete_invalid_id():
    chat_id = "bishop"
    client = TestClient(app)
    response = client.delete(f"/chats/{chat_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "Chat",
            "entity_id": chat_id
        }
    }

# --------------- get messages from chats tests --------------- #
def test_get_messages_from_chats():
    chat_id = "36b18c30f5eb4c7888229474d12e426f"
    client = TestClient(app)
    response = client.get(f"/chats/{chat_id}/messages")

    data = response.json()
    assert response.status_code == 200
    assert "count" in data["meta"]
    assert "messages" in data

    for message_data in data["messages"]:
        assert "id" in message_data
        assert "user_id" in message_data
        assert "text" in message_data
        assert "created_at" in message_data

def test_get_messages_invalid_id():
    chat_id = "0"
    client = TestClient(app)
    response = client.get(f"/chats/{chat_id}/messages")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "Chat",
            "entity_id": chat_id
        }
    }

# ------------- get users from chats tests ----------------- #
def test_get_users_from_chat():
    chat_id = "36b18c30f5eb4c7888229474d12e426f"
    client = TestClient(app)
    response = client.get(f"/chats/{chat_id}/users")
    response.status_code == 200

    data = response.json()
    assert "meta" in data
    assert "count" in data["meta"]
    assert "users" in data

    for user_data in data["users"]:
        assert "id" in user_data
        assert "created_at" in user_data

def test_get_users_invalid_id():
    chat_id = "0"
    client = TestClient(app)
    response = client.get(f"/chats/{chat_id}/users")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "type": "entity_not_found",
            "entity_name": "Chat",
            "entity_id": chat_id
        }
    }