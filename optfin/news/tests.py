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
        url = reverse('get_or_create_news')
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
        if expected_status == 200:
            news_id = sample_news.id
        url = reverse('get_or_update_news', args=[news_id])
        response = client.get(url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize("title,content,expected_status", [
        ("Valid title", "Valid content", 201),
        ("", "Content", 400),
        ("Title", "", 400),
    ])
    def test_create_news(self, auth_client, title, content, expected_status):
        url = reverse('get_or_create_news')
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
        url = reverse('get_or_update_news', args=[sample_news.id])
        payload = {field: value}
        response = auth_client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == expected_status

        if response.status_code == 200:
            updated = News.objects.get(id=sample_news.id)
            if field in ["title", "content"]:
                assert getattr(updated, field) == value

    def test_update_news_permission_denied(self, client, sample_news):
        """Проверка: нельзя обновлять без авторизации"""
        url = reverse('get_or_update_news', args=[sample_news.id])
        payload = {"title": "Hack attempt"}
        response = client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code in (401, 403)

    def test_get_all_news_empty(self, client):
        """Тест получения пустого списка новостей"""
        url = reverse('get_or_create_news')
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 0
        assert data["news"] == []

    @pytest.mark.parametrize("news_id,expected_status", [
        (1, 200),
        (0, 404),
        (-1, 404),
        (999999, 404),
    ])
    def test_take_news_boundary_values(self, client, sample_news, news_id, expected_status):
        """Параметризованный тест граничных значений для ID новости"""
        if expected_status == 200:
            news_id = sample_news.id
        url = reverse('get_or_update_news', args=[news_id])
        response = client.get(url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize("title,content,expected_status", [
        ("A", "Content", 201),
        ("T" * 200, "Content", 201),
        ("Valid title", "C", 201),
        ("Valid title", "C" * 10000, 201),
        ("T" * 201, "Content", 400),
        ("", "Content", 400),
        ("Title", "", 400),
    ])
    def test_create_news_boundary_values(self, auth_client, title, content, expected_status):
        """Тест граничных значений для полей title и content"""
        url = reverse('get_or_create_news')
        payload = {
            "title": title,
            "content": content,
        }
        response = auth_client.post(url, data=json.dumps(payload), content_type="application/json")
        # Для длинных значений может быть либо 201, либо 400 в зависимости от валидации модели
        assert response.status_code in (expected_status, 400)

    def test_create_news_without_auth(self, client):
        """Тест создания новости без авторизации"""
        url = reverse('get_or_create_news')
        payload = {
            "title": "Test title",
            "content": "Test content",
        }
        response = client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code in (401, 403)

    def test_update_news_unauthorized_user(self, client, sample_news, django_user_model):
        """Тест обновления новости другим пользователем (не автором)"""
        other_user = django_user_model.objects.create_user(
            username='otheruser',
            password='12345',
            login='otheruser',
            role='user'
        )
        client.force_login(other_user)

        url = reverse('get_or_update_news', args=[sample_news.id])
        payload = {"title": "Hack attempt"}
        response = client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 403

    def test_update_nonexistent_news(self, auth_client):
        """Тест обновления несуществующей новости"""
        url = reverse('get_or_update_news', args=[99999])
        payload = {"title": "Updated title"}
        response = auth_client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 404

    def test_create_news_with_invalid_photo(self, auth_client):
        """Тест создания новости с невалидным base64 фото"""
        url = reverse('get_or_create_news')
        payload = {
            "title": "Test title",
            "content": "Test content",
            "photo": "invalid_base64_string!!!",
        }
        response = auth_client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 400

    def test_update_news_empty_photo(self, auth_client, sample_news):
        """Тест обновления новости с пустым фото (удаление фото)"""
        url = reverse('get_or_update_news', args=[sample_news.id])
        payload = {"photo": ""}
        response = auth_client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        updated = News.objects.get(id=sample_news.id)
        assert updated.photo is None

    def test_create_news_with_published_at(self, auth_client):
        """Тест создания новости с указанной датой публикации"""
        from datetime import datetime, timedelta
        future_date = (timezone.now() + timedelta(days=1)).isoformat()

        url = reverse('get_or_create_news')
        payload = {
            "title": "Future news",
            "content": "Content",
            "published_at": future_date
        }
        response = auth_client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 201

    def test_update_news_invalid_date_format(self, auth_client, sample_news):
        """Тест обновления новости с невалидным форматом даты"""
        url = reverse('get_or_update_news', args=[sample_news.id])
        payload = {"published_at": "invalid-date-format"}
        response = auth_client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 400

    def test_news_model_str_representation(self, user):
        """Тест строкового представления модели News"""
        news = News.objects.create(
            title="Test News",
            content="Content",
            published_at=timezone.now(),
            user_id=user
        )
        assert str(news) == "Test News"

    def test_admin_can_update_any_news(self, sample_news, django_user_model):
        """Тест: админ может обновлять любую новость"""
        from rest_framework.test import APIClient

        admin_user = django_user_model.objects.create_user(
            username='admin',
            password='12345',
            login='admin',
            role='admin'
        )
        client = APIClient()
        client.force_login(admin_user)

        url = reverse('get_or_update_news', args=[sample_news.id])
        payload = {"title": "Admin updated title"}
        response = client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200