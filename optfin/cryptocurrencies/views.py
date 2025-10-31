from cryptocurrencies.models import CryptoCoin
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")


def serialize_crypto_coin(coin):
    """Сериализация криптовалюты в JSON формат"""
    return {
        "id": coin.id,
        "name": coin.name,
        "pair": coin.pair
    }


@require_http_methods(["GET"])
def get_all_cryptocurrencies(request):
    """
    Получить все криптовалюты
    """
    try:
        coins = CryptoCoin.objects.all().order_by('name')
        coins_data = [serialize_crypto_coin(coin) for coin in coins]

        logger.info(f"Retrieved {len(coins_data)} cryptocurrencies")
        return JsonResponse({
            "status": "ok",
            "count": len(coins_data),
            "cryptocurrencies": coins_data
        })
    except Exception as e:
        logger.error(f"Error getting all cryptocurrencies: {e}")
        return JsonResponse({"error": "Failed to retrieve cryptocurrencies"}, status=500)