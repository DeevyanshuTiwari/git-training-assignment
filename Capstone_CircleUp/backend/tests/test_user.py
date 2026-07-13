def test_get_current_user_profile(client, user_headers):
    response = client.get("/users/me", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"


def test_update_current_user_profile(client, user_headers):
    response = client.put(
        "/users/me",
        headers=user_headers,
        json={
            "name": "Updated Name",
            "city": "Bhopal"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_get_user_activities(client, user_headers):
    response = client.get("/users/me/activities/created", headers=user_headers)
    assert response.status_code == 200


def test_get_user_participation(client, user_headers):
    response = client.get("/users/me/activities/joined", headers=user_headers)
    assert response.status_code == 200


def test_get_user_pending_requests(client, user_headers):
    response = client.get("/users/me/participation/pending", headers=user_headers)
    assert response.status_code == 200


def test_get_user_rejected_requests(client, user_headers):
    response = client.get("/users/me/participation/rejected", headers=user_headers)
    assert response.status_code == 200
