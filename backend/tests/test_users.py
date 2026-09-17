from sqlalchemy.orm import Session

from tests.conftest import create_user, login


def test_master_can_get_user(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)
    user = create_user(db, "ana")

    response = client.get(f"/api/users/{user.id}", headers=login(client, master.username))

    assert response.status_code == 200
    assert response.json()["username"] == "ana"


def test_common_user_cannot_get_user(client, db: Session) -> None:
    user = create_user(db, "ana")
    other = create_user(db, "bia")

    response = client.get(f"/api/users/{other.id}", headers=login(client, user.username))

    assert response.status_code == 403


def test_master_can_update_user(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)
    user = create_user(db, "ana")

    response = client.put(
        f"/api/users/{user.id}",
        json={"name": "Ana Maria", "password": "new-password"},
        headers=login(client, master.username),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Ana Maria"
    assert client.post("/api/auth/login", data={"username": "ana", "password": "new-password"}).status_code == 200


def test_master_can_delete_user(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)
    user = create_user(db, "ana")

    response = client.delete(f"/api/users/{user.id}", headers=login(client, master.username))

    assert response.status_code == 204
    assert client.post("/api/auth/login", data={"username": "ana", "password": "password123"}).status_code == 401


def test_master_cannot_delete_self(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)

    response = client.delete(f"/api/users/{master.id}", headers=login(client, master.username))

    assert response.status_code == 422


def test_master_cannot_deactivate_self(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)

    response = client.put(
        f"/api/users/{master.id}",
        json={"is_active": False},
        headers=login(client, master.username),
    )

    assert response.status_code == 422
