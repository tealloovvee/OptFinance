import json
import pytest
from rest_framework.test import APIClient
from registration.models import User
from django.contrib.auth.hashers import make_password


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.parametrize(
    "payload,expected_login,expected_email",
    [
        ({"login": "user1", "email": "u1@example.com", "password": "123456"}, "user1", "u1@example.com"),
        ({"login": "user2", "email": "u2@example.com", "password": "abcdef"}, "user2", "u2@example.com"),
    ],
)
@pytest.mark.django_db
def test_register_user(client, payload, expected_login, expected_email):
    """Параметризованный тест регистрации"""
    response = client.post(
        "/registration/auth/register/",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    assert "tokens" in json_data
    assert "access_token" in json_data["tokens"]
    assert "refresh_token" in json_data["tokens"]

    user = User.objects.get(login=expected_login)
    assert user.email == expected_email
    assert user.portfolios_created == {}


@pytest.mark.parametrize(
    "login,password",
    [
        ("loginA", "pass123"),
        ("loginB", "abcdef"),
    ],
)
@pytest.mark.django_db
def test_login_user(client, login, password):
    """Параметризованный тест логина"""
    User.objects.create(
        login=login,
        email=f"{login}@example.com",
        password_hash=make_password(password),
    )

    payload = {"login": login, "password": password}
    response = client.post(
        "/registration/auth/login/",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 200
    json_data = response.json()
    assert "tokens" in json_data
    assert "access_token" in json_data["tokens"]
    assert "refresh_token" in json_data["tokens"]
    assert json_data["user"]["login"] == login


@pytest.mark.parametrize(
    "login,password",
    [
        ("profileA", "111111"),
        ("profileB", "222222"),
    ],
)
@pytest.mark.django_db
def test_get_profile_requires_auth(client, login, password):
    """Параметризованный тест получения профиля"""
    User.objects.create(
        login=login,
        email=f"{login}@example.com",
        password_hash=make_password(password)
    )

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": login, "password": password}),
        content_type="application/json"
    )

    assert login_resp.status_code == 200
    token = login_resp.json()["tokens"]["access_token"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.get("/registration/auth/profile/")
    assert resp.status_code == 200
    assert resp.json()["login"] == login
    assert resp.json()["portfolios_created"] == {}
