from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio
from registration.decorators import jwt_required
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")


def serialize_portfolio(portfolio):
    """Сериализация портфеля в JSON формат"""
    return {
        "id": portfolio.id,
        "user_id": portfolio.user.id,
        "user_login": portfolio.user.login,
        "risk": portfolio.risk,
        "annual_return": str(portfolio.annual_return),
        "is_active": portfolio.is_active,
        "created_at": portfolio.created_at.isoformat()
    }


@api_view(['GET'])
@jwt_required
def get_all_portfolios(request):
    """
    Получить все портфели текущего пользователя
    """
    try:
        user = request.user
        portfolios = Portfolio.objects.filter(user=user).order_by('-created_at')
        portfolios_data = [serialize_portfolio(portfolio) for portfolio in portfolios]

        logger.info(f"Retrieved {len(portfolios_data)} portfolios for user {user.id}")
        return Response({
            "status": "ok",
            "count": len(portfolios_data),
            "portfolios": portfolios_data
        })
    except Exception as e:
        logger.error(f"Error getting all portfolios: {e}")
        return Response({"error": "Failed to retrieve portfolios"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@jwt_required
def get_portfolio(request, portfolio_id):
    """Получить портфель по ID"""
    try:
        user = request.user
        portfolio = Portfolio.objects.get(id=portfolio_id, user=user)
        return Response(serialize_portfolio(portfolio))
    except Portfolio.DoesNotExist:
        logger.error(f"Portfolio not found: {portfolio_id}")
        return Response({"error": "Portfolio not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving portfolio {portfolio_id}: {e}")
        return Response({"error": "Failed to retrieve portfolio"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@jwt_required
def create_portfolio(request):
    """Создать новый портфель"""
    try:
        user = request.user
        data = request.data
        
        risk = data.get('risk')
        annual_return = data.get('annual_return', 0)
        
        if not risk:
            return Response({"error": "Risk is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        portfolio = Portfolio.objects.create(
            user=user,
            risk=risk,
            annual_return=annual_return,
            is_active=True
        )
        
        logger.info(f"Created portfolio {portfolio.id} for user {user.id}")
        return Response(serialize_portfolio(portfolio), status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        return Response({"error": "Failed to create portfolio"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
