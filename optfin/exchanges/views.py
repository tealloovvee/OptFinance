from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Exchange
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")


def serialize_exchange(exchange):
    """Сериализация биржи в JSON формат"""
    return {
        "id": exchange.id,
        "name": exchange.name,
        "trading_volume": str(exchange.trading_volume),
        "coins_listed": exchange.coins_listed,
        "rating": str(exchange.rating)
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_exchanges(request):
    """
    Получить все биржи
    """
    try:
        exchanges = Exchange.objects.all().order_by('name')
        exchanges_data = [serialize_exchange(exchange) for exchange in exchanges]

        logger.info(f"Retrieved {len(exchanges_data)} exchanges")
        return Response({
            "status": "ok",
            "count": len(exchanges_data),
            "exchanges": exchanges_data
        })
    except Exception as e:
        logger.error(f"Error getting all exchanges: {e}")
        return Response({"error": "Failed to retrieve exchanges"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_exchange(request, exchange_id):
    """Получить биржу по ID"""
    try:
        exchange = Exchange.objects.get(id=exchange_id)
        return Response(serialize_exchange(exchange))
    except Exchange.DoesNotExist:
        logger.error(f"Exchange not found: {exchange_id}")
        return Response({"error": "Exchange not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving exchange {exchange_id}: {e}")
        return Response({"error": "Failed to retrieve exchange"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
