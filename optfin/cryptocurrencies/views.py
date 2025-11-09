from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import CryptoCoin
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_cryptocurrencies(request):
    """
    Получить все криптовалюты
    """
    try:
        coins = CryptoCoin.objects.all().order_by('name')
        coins_data = [serialize_crypto_coin(coin) for coin in coins]

        logger.info(f"Retrieved {len(coins_data)} cryptocurrencies")
        return Response({
            "status": "ok",
            "count": len(coins_data),
            "cryptocurrencies": coins_data
        })
    except Exception as e:
        logger.error(f"Error getting all cryptocurrencies: {e}")
        return Response({"error": "Failed to retrieve cryptocurrencies"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_crypto_coin(request, coin_id):
    """Получить криптовалюту по ID"""
    try:
        coin = CryptoCoin.objects.get(id=coin_id)
        return Response(serialize_crypto_coin(coin))
    except CryptoCoin.DoesNotExist:
        logger.error(f"CryptoCoin not found: {coin_id}")
        return Response({"error": "CryptoCoin not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving CryptoCoin {coin_id}: {e}")
        return Response({"error": "Failed to retrieve CryptoCoin"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
