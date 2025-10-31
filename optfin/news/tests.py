import base64
import json
import pytest
from django.urls import reverse
from django.utils import timezone
from news.models import News

@pytest.mark.django_db
class TestNewsAPI:

    @pytest.fixture
    def user(self, django_user_model):
        """Создаём тестового пользователя"""
        return django_user_model.objects.create_user(
            username='testuser',
            password='12345',
            login='testuser',
            role='user'
        )

    @pytest.fixture
    def auth_client(self, client, user):
        """Авторизованный клиент с JWT (если jwt_required требует токен)"""
        client.force_login(user)
        return client

    @pytest.fixture
    def sample_news(self, user):
        """Создаём тестовую новость"""
        return News.objects.create(
            title="Test title",
            content="Test content",
            published_at=timezone.now(),
            photo=None,
            user_id=user
        )

    def test_get_all_news(self, client, sample_news):
        url = reverse('get_all_news')
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "news" in data
        assert len(data["news"]) >= 1
        assert data["news"][0]["title"] == sample_news.title

    @pytest.mark.parametrize("news_id,expected_status", [
        (1, 200),
        (999, 404),
    ])
    def test_take_news(self, client, sample_news, news_id, expected_status):
        url = reverse('take_news', args=[news_id])
        response = client.get(url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize("title,content,expected_status", [
        ("Valid title", "Valid content", 201),
        ("", "Content", 400),
        ("Title", "", 400),
    ])
    def test_create_news(self, auth_client, title, content, expected_status):
        url = reverse('create_news')
        payload = {
            "title": title,
            "content": content,
            "photo": base64.b64encode(b"fake image").decode('utf-8'),
        }
        response = auth_client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize("field, value, expected_status", [
        ("title", "Updated title", 200),
        ("content", "Updated content", 200),
        ("photo", base64.b64encode(b"new img").decode('utf-8'), 200),
        ("published_at", timezone.now().isoformat(), 200),
    ])
    def test_update_news(self, auth_client, sample_news, field, value, expected_status):
        url = reverse('update_news', args=[sample_news.id])
        payload = {field: value}
        response = auth_client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == expected_status

        if response.status_code == 200:
            updated = News.objects.get(id=sample_news.id)
            if field in ["title", "content"]:
                assert getattr(updated, field) == value

    def test_update_news_permission_denied(self, client, sample_news):
        """Проверка: нельзя обновлять без авторизации"""
        url = reverse('update_news', args=[sample_news.id])
        payload = {"title": "Hack attempt"}
        response = client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code in (401, 403)
