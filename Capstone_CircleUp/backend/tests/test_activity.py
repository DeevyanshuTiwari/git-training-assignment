from datetime import date, datetime, timedelta


def test_create_activity_success(client, user_headers):
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "Test Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": future_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 10
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Activity"


def test_create_activity_past_date_fails(client, user_headers):
    past_date = date.today() - timedelta(days=1)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "Test Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": past_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 10
        }
    )
    assert response.status_code == 400
    assert "future" in response.json()["detail"].lower()


def test_create_activity_zero_participants_fails(client, user_headers):
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "Test Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": future_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 0
        }
    )
    assert response.status_code == 422  # Pydantic validation error


def test_edit_activity_non_owner_fails(client, user_headers, create_test_user, db_session):
    other_user = create_test_user(email="other@test.com")

    from app.models.activity import Activity
    from app.enums.activity_status import ActivityStatus
    act = Activity(
        title="Other Activity",
        description="Three Words Here",
        category="Tech",
        location="Indore",
        activity_date=date.today() + timedelta(days=5),
        activity_time=datetime.now().time(),
        max_participants=5,
        status=ActivityStatus.OPEN,
        created_by=other_user.id
    )
    db_session.add(act)
    db_session.commit()
    db_session.refresh(act)

    response = client.put(
        f"/activities/{act.id}",
        headers=user_headers,
        json={
            "title": "Hacked Title"
        }
    )
    assert response.status_code == 403


def test_cancel_activity_non_owner_fails(client, user_headers, create_test_user, db_session):
    other_user = create_test_user(email="other2@test.com")
    from app.models.activity import Activity
    from app.enums.activity_status import ActivityStatus
    act = Activity(
        title="Other Activity 2",
        description="Three Words Here",
        category="Tech",
        location="Indore",
        activity_date=date.today() + timedelta(days=5),
        activity_time=datetime.now().time(),
        max_participants=5,
        status=ActivityStatus.OPEN,
        created_by=other_user.id
    )
    db_session.add(act)
    db_session.commit()
    db_session.refresh(act)

    response = client.put(
        f"/activities/{act.id}/cancel",
        headers=user_headers
    )
    assert response.status_code == 403


def test_cancel_activity_owner_success(client, user_headers):
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "My Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": future_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 10
        }
    )
    act_id = response.json()["id"]

    cancel_response = client.put(
        f"/activities/{act_id}/cancel",
        headers=user_headers
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"


def test_get_activities(client, db_session):
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activity_by_id(client, user_headers):
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "Get Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": future_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 10
        }
    )
    act_id = response.json()["id"]
    get_res = client.get(f"/activities/{act_id}")
    assert get_res.status_code == 200


def test_update_activity(client, user_headers):
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "Update Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": future_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 10
        }
    )
    act_id = response.json()["id"]
    up_res = client.put(f"/activities/{act_id}", headers=user_headers, json={"title": "Updated Title"})
    assert up_res.status_code == 200
    assert up_res.json()["title"] == "Updated Title"


def test_get_organizer_contact(client, user_headers):
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/activities",
        headers=user_headers,
        json={
            "title": "Contact Activity",
            "description": "Test Description Words",
            "category": "Tech",
            "location": "Indore",
            "activity_date": future_date.isoformat(),
            "activity_time": "14:00:00",
            "max_participants": 10
        }
    )
    act_id = response.json()["id"]
    contact_res = client.get(f"/activities/{act_id}/organizer-contact", headers=user_headers)
    assert contact_res.status_code in [200, 403]
