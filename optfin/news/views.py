from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from news.models import News
from registration.decorators import jwt_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import base64
import logging
import json

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


@api_view(['GET'])
def get_all_news(request):
    """Получить все новости"""
    try:
        news_list = News.objects.all().order_by('-published_at')
        news_data = [serialize_news(news) for news in news_list]
        logger.info(f"Retrieved {len(news_data)} news items")
        return Response({
            "status": "ok",
            "count": len(news_data),
            "news": news_data
        })
    except Exception as e:
        logger.error(f"Error getting all news: {e}")
        return Response({"error": "Failed to retrieve news"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def take_news(request, news_id):
    """Получить одну новость по ID"""
    try:
        news = get_object_or_404(News, id=news_id)
        return Response({
            "status": "ok",
            "news": serialize_news(news)
        })
    except Exception as e:
        logger.error(f"Error getting news {news_id}: {e}")
        return Response({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@jwt_required
def create_news(request):
    """Создать новость (требуется аутентификация)"""
    try:
        data = request.data
        title = data.get('title')
        content = data.get('content')
        photo_base64 = data.get('photo')
        published_at = data.get('published_at')

        if not title or not content:
            return Response({"error": "Missing required fields: title and content"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        photo_binary = None
        if photo_base64:
            try:
                photo_binary = base64.b64decode(photo_base64)
            except Exception as e:
                logger.error(f"Error decoding photo: {e}")
                return Response({"error": "Invalid photo format"}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({
            "status": "ok",
            "message": "News created successfully",
            "news": serialize_news(news)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating news: {e}")
        return Response({"error": "Failed to create news"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@jwt_required
def update_news(request, news_id):
    """Обновить новость (требуется аутентификация, только автор или админ)"""
    try:
        news = get_object_or_404(News, id=news_id)
        user = request.user

        if news.user_id.id != user.id and user.role != 'admin':
            logger.warning(f"User {user.id} tried to update news {news_id} without permission")
            return Response({"error": "Permission denied. You can only edit your own news."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
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
                    return Response({"error": "Invalid photo format"}, status=status.HTTP_400_BAD_REQUEST)
        if published_at is not None:
            try:
                from datetime import datetime
                news.published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error parsing published_at: {e}")
                return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        news.save()
        logger.info(f"News {news_id} updated by user {user.id}")
        return Response({
            "status": "ok",
            "message": "News updated successfully",
            "news": serialize_news(news)
        })

    except Exception as e:
        logger.error(f"Error updating news {news_id}: {e}")
        return Response({"error": "Failed to update news"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
