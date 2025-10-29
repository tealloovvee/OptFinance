import json
import logging
from django.test import TestCase
from rest_framework.test import APIClient
from registration.models import User
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")

class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Тест регистрации нового пользователя"""
        payload = {"login": "testuser", "email": "test@example.com", "password": "123456"}
        response = self.client.post(
            '/registration/auth/register/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("tokens", json_data)
        self.assertIn("access_token", json_data["tokens"])
        self.assertIn("refresh_token", json_data["tokens"])
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.login, "testuser")
        self.assertEqual(user.portfolios_created, {})

    def test_login_user(self):
        """Тест логина существующего пользователя"""
        user = User.objects.create(
            login="testuser",
            email="test@example.com",
            password_hash=make_password("123456")
        )
        payload = {"login": "testuser", "password": "123456"}
        response = self.client.post(
            "/registration/auth/login/",
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("tokens", json_data)
        self.assertIn("access_token", json_data["tokens"])
        self.assertIn("refresh_token", json_data["tokens"])
        self.assertEqual(json_data["user"]["login"], "testuser")
        self.assertEqual(json_data["user"]["portfolios_created"], {})

    def test_get_profile_requires_auth(self):
        """Тест получения профиля с JWT авторизацией"""
        user = User.objects.create(
            login="testuser",
            email="test@example.com",
            password_hash=make_password("123456")
        )
        # логинимся, чтобы получить токен
        login_resp = self.client.post(
            "/registration/auth/login/",
            data=json.dumps({"login": "testuser", "password": "123456"}),
            content_type='application/json'
        )
        self.assertEqual(login_resp.status_code, 200, login_resp.content)
        token = login_resp.json()["tokens"]["access_token"]  # исправлено

        # авторизация с токеном
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get("/registration/auth/profile/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["login"], "testuser")
        self.assertEqual(resp.json()["portfolios_created"], {})
