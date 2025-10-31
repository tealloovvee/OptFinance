from exchanges.models import Exchange
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def serialize_exchange(exchange):
    """Сериализация биржи в JSON формат"""
    return {
        "id": exchange.id,
        "name": exchange.name,
        "trading_volume": str(exchange.trading_volume),
        "coins_listed": exchange.coins_listed,
        "rating": str(exchange.rating)
    }


@require_http_methods(["GET"])
def get_all_exchanges(request):
    """
    Получить все биржи
    """
    try:
        exchanges = Exchange.objects.all().order_by('name')
        exchanges_data = [serialize_exchange(exchange) for exchange in exchanges]

        logger.info(f"Retrieved {len(exchanges_data)} exchanges")
        return JsonResponse({
            "status": "ok",
            "count": len(exchanges_data),
            "exchanges": exchanges_data
        })
    except Exception as e:
        logger.error(f"Error getting all exchanges: {e}")
        return JsonResponse({"error": "Failed to retrieve exchanges"}, status=500)