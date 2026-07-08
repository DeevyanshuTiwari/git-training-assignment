from datetime import date, datetime, timedelta


def test_duplicate_participation_fails(client, user_headers, create_test_user, db_session):
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

    response1 = client.post(
        f"/participation/activities/{act.id}/request",
        headers=user_headers
    )
    assert response1.status_code == 201

    response2 = client.post(
        f"/participation/activities/{act.id}/request",
        headers=user_headers
    )
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


def test_get_activity_participants(client, user_headers):
    act_res = client.post("/activities", headers=user_headers, json={
        "title": "Participants Activity", "description": "Three Words Here",
        "category": "Tech", "location": "Indore", "activity_date": (date.today() + timedelta(days=5)).isoformat(),
        "activity_time": "14:00:00", "max_participants": 10
    })
    act_id = act_res.json()["id"]
    client.post(f"/participation/activities/{act_id}/request", headers=user_headers)
    get_res = client.get(f"/activities/{act_id}/participants", headers=user_headers)
    assert get_res.status_code == 200


def test_cancel_participation(client, user_headers, create_test_user):
    act_res = client.post("/activities", headers=user_headers, json={
        "title": "Cancel Part Activity", "description": "Three Words Here",
        "category": "Tech", "location": "Indore", "activity_date": (date.today() + timedelta(days=5)).isoformat(),
        "activity_time": "14:00:00", "max_participants": 10
    })
    act_id = act_res.json()["id"]

    other_user = create_test_user(email="req@test.com")
    from app.core.security import create_access_token
    other_token = create_access_token(data={"sub": other_user.email})
    other_headers = {"Authorization": f"Bearer {other_token}"}

    req_res = client.post(f"/participation/activities/{act_id}/request", headers=other_headers)
    part_id = req_res.json()["id"]
    del_res = client.delete(f"/participation/requests/{part_id}", headers=other_headers)
    assert del_res.status_code == 204


def test_capacity_logic_auto_full(client, user_headers, create_test_user, db_session):
    # Setup activity with 1 max participant created by current user
    from app.models.activity import Activity
    from app.models.user import User
    from app.enums.activity_status import ActivityStatus

    # Get current user from db (test@test.com)
    current_user = db_session.query(User).filter(User.email == "test@test.com").first()

    act = Activity(
        title="1 Spot Activity",
        description="Three Words Here",
        category="Tech",
        location="Indore",
        activity_date=date.today() + timedelta(days=5),
        activity_time=datetime.now().time(),
        max_participants=1,
        status=ActivityStatus.OPEN,
        created_by=current_user.id
    )
    db_session.add(act)
    db_session.commit()
    db_session.refresh(act)

    # other user requests participation
    other_user = create_test_user(email="other@test.com")
    from app.core.security import create_access_token
    other_token = create_access_token(data={"sub": other_user.email})

    req_response = client.post(
        f"/participation/activities/{act.id}/request",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert req_response.status_code == 201
    req_id = req_response.json()["id"]

    # current_user approves
    approve_res = client.put(
        f"/participation/requests/{req_id}/approve",
        headers=user_headers
    )
    assert approve_res.status_code == 200

    # check if activity is FULL
    db_session.refresh(act)
    assert act.status == ActivityStatus.FULL

    # third user tries to request
    third_user = create_test_user(email="third@test.com")
    third_token = create_access_token(data={"sub": third_user.email})
    req3_res = client.post(
        f"/participation/activities/{act.id}/request",
        headers={"Authorization": f"Bearer {third_token}"}
    )
    assert req3_res.status_code == 400
    assert "full" in req3_res.json()["detail"].lower()


def test_approve_reject_non_owner_fails(client, user_headers, create_test_user, db_session):
    other_user = create_test_user(email="owner@test.com")
    from app.models.activity import Activity
    from app.enums.activity_status import ActivityStatus
    act = Activity(
        title="Owner Activity",
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

    # current_user requests
    req_response = client.post(
        f"/participation/activities/{act.id}/request",
        headers=user_headers
    )
    req_id = req_response.json()["id"]

    # third user tries to approve
    third_user = create_test_user(email="third@test.com")
    from app.core.security import create_access_token
    third_token = create_access_token(data={"sub": third_user.email})

    approve_res = client.put(
        f"/participation/requests/{req_id}/approve",
        headers={"Authorization": f"Bearer {third_token}"}
    )
    assert approve_res.status_code == 403

    reject_res = client.put(
        f"/participation/requests/{req_id}/reject",
        headers={"Authorization": f"Bearer {third_token}"}
    )
    assert reject_res.status_code == 403
