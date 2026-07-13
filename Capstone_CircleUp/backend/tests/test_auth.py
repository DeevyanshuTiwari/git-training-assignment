def test_register_user_success(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@test.com",
            "name": "New User",
            "password": "Password@123",
            "phone_number": "9998887776",
            "city": "Mumbai",
            "bio": "Hello World This"
        }
    )
    assert response.status_code == 200


def test_register_user_duplicate_email(client, create_test_user):
    create_test_user(email="dup@test.com")
    response = client.post(
        "/auth/register",
        json={
            "email": "dup@test.com",
            "name": "Another User",
            "password": "Password@123",
            "phone_number": "9998887776",
            "city": "Mumbai",
            "bio": "Hello World This"
        }
    )
    assert response.status_code == 400


def test_login_success(client, create_test_user):
    create_test_user(email="login@test.com")
    response = client.post(
        "/auth/login",
        data={
            "username": "login@test.com",
            "password": "Password@123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client, create_test_user):
    create_test_user(email="login2@test.com")
    response = client.post(
        "/auth/login",
        data={
            "username": "login2@test.com",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
