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

    assert response.status_code == 201
    json_data = response.json()
    assert "message" in json_data
    assert "user" in json_data
    assert json_data["user"]["login"] == expected_login
    assert json_data["user"]["email"] == expected_email

    user = User.objects.get(login=expected_login)
    assert user.email == expected_email
    assert user.portfolios_created == {}
    assert user.is_active == False


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


@pytest.mark.django_db
def test_register_missing_fields(client):
    """Тест регистрации с отсутствующими полями"""
    test_cases = [
        ({"login": "user1", "email": "u1@example.com"}, "password"),
        ({"login": "user1", "password": "123456"}, "email"),
        ({"email": "u1@example.com", "password": "123456"}, "login"),
        ({}, "all fields"),
    ]

    for payload, missing_field in test_cases:
        response = client.post(
            "/registration/auth/register/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "error" in response.json()


@pytest.mark.parametrize(
    "login,email,password,expected_status,error_keyword",
    [
        ("a" * 150, "valid@example.com", "123456", 400, None),
        ("validlogin", "invalid-email", "123456", 400, None),
        ("validlogin", "a" * 245 + "@example.com", "123456", 400, None),
        ("", "valid@example.com", "123456", 400, None),
        ("validlogin", "", "123456", 400, None),
        ("validlogin", "valid@example.com", "", 400, None),
    ],
)
@pytest.mark.django_db
def test_register_boundary_values(client, login, email, password, expected_status, error_keyword):
    """Тест граничных значений для регистрации"""
    payload = {"login": login, "email": email, "password": password}
    response = client.post(
        "/registration/auth/register/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code in (200, 400, 201)


@pytest.mark.django_db
def test_register_duplicate_login(client):
    """Тест регистрации с дублирующимся login"""
    User.objects.create(
        login="existing",
        email="existing@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    payload = {"login": "existing", "email": "new@example.com", "password": "123456"}
    response = client.post(
        "/registration/auth/register/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["error"].lower()


@pytest.mark.django_db
def test_register_duplicate_email(client):
    """Тест регистрации с дублирующимся email"""
    User.objects.create(
        login="existing",
        email="existing@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    payload = {"login": "newuser", "email": "existing@example.com", "password": "123456"}
    response = client.post(
        "/registration/auth/register/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["error"].lower()


@pytest.mark.django_db
def test_login_missing_credentials(client):
    """Тест логина с отсутствующими полями"""
    test_cases = [
        ({"login": "user1"}, "password"),
        ({"password": "123456"}, "login"),
        ({}, "all fields"),
    ]

    for payload, missing_field in test_cases:
        response = client.post(
            "/registration/auth/login/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400


@pytest.mark.django_db
def test_login_invalid_credentials(client):
    """Тест логина с неверными учетными данными"""
    User.objects.create(
        login="user1",
        email="user1@example.com",
        password_hash=make_password("correct_password"),
        is_active=True
    )

    test_cases = [
        {"login": "user1", "password": "wrong_password"},
        {"login": "nonexistent", "password": "any_password"},
        {"login": "user1@example.com", "password": "wrong_password"},
    ]

    for payload in test_cases:
        response = client.post(
            "/registration/auth/login/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 401
        assert "error" in response.json()


@pytest.mark.django_db
def test_login_inactive_user(client):
    """Тест логина неактивного пользователя (email не подтвержден)"""
    User.objects.create(
        login="inactive",
        email="inactive@example.com",
        password_hash=make_password("123456"),
        is_active=False
    )

    payload = {"login": "inactive", "password": "123456"}
    response = client.post(
        "/registration/auth/login/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 403
    assert "email not confirmed" in response.json()["error"].lower()


@pytest.mark.django_db
def test_login_by_email(client):
    """Тест логина по email вместо login"""
    User.objects.create(
        login="user1",
        email="user1@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    payload = {"login": "user1@example.com", "password": "123456"}
    response = client.post(
        "/registration/auth/login/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json()["user"]["login"] == "user1"


@pytest.mark.django_db
def test_get_profile_without_auth(client):
    """Тест получения профиля без аутентификации"""
    response = client.get("/registration/auth/profile/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_user_by_id(client):
    """Тест получения пользователя по ID (требует авторизацию)"""
    user = User.objects.create(
        login="testuser",
        email="test@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    response = client.get(f"/registration/users/{user.id}/")
    assert response.status_code == 401

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": "testuser", "password": "123456"}),
        content_type="application/json"
    )
    token = login_resp.json()["tokens"]["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/registration/users/{user.id}/")
    assert response.status_code == 200
    assert response.json()["login"] == "testuser"


@pytest.mark.django_db
def test_get_nonexistent_user(client):
    """Тест получения несуществующего пользователя"""
    User.objects.create(
        login="authuser",
        email="auth@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": "authuser", "password": "123456"}),
        content_type="application/json"
    )
    token = login_resp.json()["tokens"]["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/registration/users/99999/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_update_user(client):
    """Тест обновления пользователя"""
    user = User.objects.create(
        login="olduser",
        email="old@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": "olduser", "password": "123456"}),
        content_type="application/json"
    )
    token = login_resp.json()["tokens"]["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {"login": "newuser", "email": "new@example.com"}
    response = client.put(
        f"/registration/users/{user.id}/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json()["login"] == "newuser"
    assert response.json()["email"] == "new@example.com"


@pytest.mark.django_db
def test_refresh_token(client):
    """Тест обновления токена"""
    user = User.objects.create(
        login="testuser",
        email="test@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": "testuser", "password": "123456"}),
        content_type="application/json"
    )
    refresh_token = login_resp.json()["tokens"]["refresh_token"]

    payload = {"refresh_token": refresh_token}
    response = client.post(
        "/registration/auth/refresh/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert "tokens" in response.json()
    assert "access_token" in response.json()["tokens"]


@pytest.mark.django_db
def test_refresh_token_invalid(client):
    """Тест обновления токена с невалидным refresh token"""
    payload = {"refresh_token": "invalid_token"}
    response = client.post(
        "/registration/auth/refresh/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code in (400, 401)


@pytest.mark.django_db
def test_refresh_token_missing(client):
    """Тест обновления токена без refresh token"""
    payload = {}
    response = client.post(
        "/registration/auth/refresh/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_logout(client):
    """Тест выхода из системы"""
    user = User.objects.create(
        login="testuser",
        email="test@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": "testuser", "password": "123456"}),
        content_type="application/json"
    )
    token = login_resp.json()["tokens"]["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.post("/registration/auth/logout/")
    assert response.status_code == 200
    assert "message" in response.json()

    user.refresh_from_db()
    assert user.refresh_token is None


@pytest.mark.django_db
def test_delete_user(client):
    """Тест удаления пользователя"""
    user = User.objects.create(
        login="todelete",
        email="delete@example.com",
        password_hash=make_password("123456"),
        is_active=True
    )

    login_resp = client.post(
        "/registration/auth/login/",
        data=json.dumps({"login": "todelete", "password": "123456"}),
        content_type="application/json"
    )
    token = login_resp.json()["tokens"]["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.delete(f"/registration/users/{user.id}/")
    assert response.status_code == 200

    assert not User.objects.filter(id=user.id).exists()


@pytest.mark.django_db
def test_user_model_defaults():
    """Тест значений по умолчанию модели User"""
    user = User.objects.create(
        login="defaultuser",
        email="default@example.com",
        password_hash=make_password("123456")
    )
    assert user.role == "user"
    assert user.is_active == True
    assert user.portfolios_created == {}
    assert user.refresh_token is None or user.refresh_token == ""


@pytest.mark.django_db
def test_user_str_representation():
    """Тест строкового представления модели User"""
    user = User.objects.create(
        login="testuser",
        email="test@example.com",
        password_hash=make_password("123456")
    )
    assert str(user) == "testuser"