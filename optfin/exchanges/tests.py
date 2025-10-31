import pytest
from exchanges.models import Exchange
from rest_framework.test import APIClient
from decimal import Decimal


@pytest.fixture
def client():
    """Фикстура для клиента API"""
    return APIClient()

@pytest.mark.parametrize(
    "exchanges_input,expected_count",
    [
        (
            [
                ("Binance", Decimal("1234567890.1234567890"), 350, Decimal("9.8")),
                ("Kraken", Decimal("987654321.9876543210"), 210, Decimal("8.7")),
            ],
            2
        ),
        (
            [
                ("Bybit", Decimal("55555555.5555555555"), 120, Decimal("7.5")),
                ("OKX", Decimal("77777777.7777777777"), 180, Decimal("8.0")),
                ("KuCoin", Decimal("33333333.3333333333"), 150, Decimal("8.3")),
            ],
            3
        ),
    ],
)

@pytest.mark.django_db
def test_get_all_exchanges(client, exchanges_input, expected_count):
    """
    Параметризованный тест получения списка всех бирж
    """
    for name, volume, coins, rating in exchanges_input:
        Exchange.objects.create(
            name=name,
            trading_volume=volume,
            coins_listed=coins,
            rating=rating
        )

    response = client.get("/exchanges/")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["count"] == expected_count
    assert len(data["exchanges"]) == expected_count

    returned_names = {exchange["name"] for exchange in data["exchanges"]}
    for name, _, _, _ in exchanges_input:
        assert name in returned_names


@pytest.mark.django_db
def test_get_all_exchanges_empty(client):
    """
    Проверка, что при отсутствии бирж возвращается пустой список
    """
    response = client.get("/exchanges/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["count"] == 0
    assert data["exchanges"] == []
