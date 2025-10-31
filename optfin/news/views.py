from news.models import News
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from registration.decorators import jwt_required
from django.utils import timezone
import json
import logging
import base64

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")


def serialize_news(news_item):
    """Сериализация новости в JSON формат"""
    photo_data = None
    if news_item.photo:
        try:
            photo_data = base64.b64encode(news_item.photo).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding photo for news {news_item.id}: {e}")

    return {
        "id": news_item.id,
        "title": news_item.title,
        "content": news_item.content,
        "published_at": news_item.published_at.isoformat() if news_item.published_at else None,
        "photo": photo_data,
        "user_id": news_item.user_id.id,
        "user_login": news_item.user_id.login
    }


@require_http_methods(["GET"])
def get_all_news(request):
    """
    Получить все новости
    """
    try:
        news_list = News.objects.all().order_by('-published_at')
        news_data = [serialize_news(news) for news in news_list]

        logger.info(f"Retrieved {len(news_data)} news items")
        return JsonResponse({
            "status": "ok",
            "count": len(news_data),
            "news": news_data
        })
    except Exception as e:
        logger.error(f"Error getting all news: {e}")
        return JsonResponse({"error": "Failed to retrieve news"}, status=500)


@require_http_methods(["GET"])
def take_news(request, news_id):
    """
    Получить одну новость по ID
    """
    try:
        news = get_object_or_404(News, id=news_id)
        news_data = serialize_news(news)

        logger.info(f"Retrieved news {news_id}")
        return JsonResponse({
            "status": "ok",
            "news": news_data
        })
    except Exception as e:
        logger.error(f"Error getting news {news_id}: {e}")
        return JsonResponse({"error": "News not found"}, status=404)


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def create_news(request):
    """
    Создать новость (требуется аутентификация)
    """
    try:
        data = json.loads(request.body) if request.body else request.POST

        title = data.get('title')
        content = data.get('content')
        photo_base64 = data.get('photo', None)
        published_at = data.get('published_at', None)

        if not title or not content:
            return JsonResponse({"error": "Missing required fields: title and content"}, status=400)

        user = request.user

        photo_binary = None
        if photo_base64:
            try:
                photo_binary = base64.b64decode(photo_base64)
            except Exception as e:
                logger.error(f"Error decoding photo: {e}")
                return JsonResponse({"error": "Invalid photo format"}, status=400)

        if published_at:
            try:
                from datetime import datetime
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error parsing published_at: {e}")
                published_at = timezone.now()
        else:
            published_at = timezone.now()

        news = News.objects.create(
            title=title,
            content=content,
            published_at=published_at,
            photo=photo_binary,
            user_id=user
        )

        logger.info(f"News created: {news.id} by user {user.id}")
        return JsonResponse({
            "status": "ok",
            "message": "News created successfully",
            "news": serialize_news(news)
        }, status=201)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error creating news: {e}")
        return JsonResponse({"error": "Failed to create news"}, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["PUT", "PATCH"])
def update_news(request, news_id):
    """
    Обновить новость (требуется аутентификация, только автор или админ)
    """
    try:
        news = get_object_or_404(News, id=news_id)
        user = request.user

        if news.user_id.id != user.id and user.role != 'admin':
            logger.warning(f"User {user.id} tried to update news {news_id} without permission")
            return JsonResponse({"error": "Permission denied. You can only edit your own news."}, status=403)

        data = json.loads(request.body) if request.body else request.POST

        title = data.get('title')
        content = data.get('content')
        photo_base64 = data.get('photo')
        published_at = data.get('published_at')

        if title is not None:
            news.title = title

        if content is not None:
            news.content = content

        if photo_base64 is not None:
            if photo_base64 == "" or photo_base64 is None:
                news.photo = None
            else:
                try:
                    news.photo = base64.b64decode(photo_base64)
                except Exception as e:
                    logger.error(f"Error decoding photo: {e}")
                    return JsonResponse({"error": "Invalid photo format"}, status=400)

        if published_at is not None:
            try:
                from datetime import datetime
                news.published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error parsing published_at: {e}")
                return JsonResponse({"error": "Invalid date format"}, status=400)

        news.save()

        logger.info(f"News {news_id} updated by user {user.id}")
        return JsonResponse({
            "status": "ok",
            "message": "News updated successfully",
            "news": serialize_news(news)
        })

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error updating news {news_id}: {e}")
        return JsonResponse({"error": "Failed to update news"}, status=500)