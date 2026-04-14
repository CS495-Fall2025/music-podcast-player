from rss_music_data_model import Base, get_engine, User


def _setup_db(db_session):
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def test_get_privacy_returns_false_by_default(client, db_session):
    user = User(username="alice", email="alice@example.com", password=b"password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.get(f"/users/{user.id}/privacy")

    assert response.status_code == 200
    assert response.json()["profile_public"] is False


def test_get_privacy_returns_false_when_private(client, db_session):
    user = User(
        username="bob",
        email="bob@example.com",
        password=b"password123",
        profile_public=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.get(f"/users/{user.id}/privacy")

    assert response.status_code == 200
    assert response.json()["profile_public"] is False


def test_patch_privacy_sets_to_false(client, db_session):
    user = User(username="carol", email="carol@example.com", password=b"password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.patch(f"/users/{user.id}/privacy", json={"profile_public": False})

    assert response.status_code == 200
    assert response.json()["profile_public"] is False

    db_session.refresh(user)
    assert user.profile_public is False


def test_patch_privacy_sets_to_true(client, db_session):
    user = User(
        username="dave",
        email="dave@example.com",
        password=b"password123",
        profile_public=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.patch(f"/users/{user.id}/privacy", json={"profile_public": True})

    assert response.status_code == 200
    assert response.json()["profile_public"] is True

    db_session.refresh(user)
    assert user.profile_public is True


def test_patch_privacy_rejects_non_boolean(client, db_session):
    response = client.patch("/users/1/privacy", json={"profile_public": "yes"})

    assert response.status_code == 400
    assert response.json()["error"] == "InvalidArgument"
