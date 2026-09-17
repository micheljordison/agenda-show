from sqlalchemy.orm import Session

from tests.conftest import create_appointment, create_user, login


def test_common_user_only_lists_linked_appointments(client, db: Session) -> None:
    user_a = create_user(db, "ana")
    user_b = create_user(db, "bia")
    create_appointment(db, "Compromisso Ana", user_a)
    create_appointment(db, "Compromisso Bia", user_b)

    response = client.get("/api/appointments", headers=login(client, "ana"))

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles == ["Compromisso Ana"]


def test_master_lists_all_appointments(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)
    user = create_user(db, "ana")
    create_appointment(db, "Compromisso Master", master)
    create_appointment(db, "Compromisso Ana", user)

    response = client.get("/api/appointments", headers=login(client, "master"))

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert titles == {"Compromisso Master", "Compromisso Ana"}


def test_common_user_cannot_unlink_another_user(client, db: Session) -> None:
    user_a = create_user(db, "ana")
    user_b = create_user(db, "bia")
    appointment = create_appointment(db, "Compromisso Ana", user_a)

    response = client.delete(
        f"/api/appointments/{appointment.id}/users/{user_b.id}",
        headers=login(client, "ana"),
    )

    assert response.status_code == 403


def test_master_can_unlink_any_user(client, db: Session) -> None:
    master = create_user(db, "master", is_master=True)
    user = create_user(db, "ana")
    appointment = create_appointment(db, "Compromisso Ana", user)

    response = client.delete(
        f"/api/appointments/{appointment.id}/users/{user.id}",
        headers=login(client, "master"),
    )

    assert response.status_code == 204
