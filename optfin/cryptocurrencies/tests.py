import pytest
from cryptocurrencies.models import CryptoCoin
from rest_framework.test import APIClient


@pytest.fixture
def client():
    """Фикстура для клиента API"""
    return APIClient()

@pytest.mark.parametrize(
    "coins_input,expected_count",
    [
        (
            [("Bitcoin", "BTC/USD"), ("Ethereum", "ETH/USD")],
            2
        ),
        (
            [("TON", "TON/USDT"), ("Dogecoin", "DOGE/USD"), ("Litecoin", "LTC/USD")],
            3
        ),
    ],
)
@pytest.mark.django_db
def test_get_all_cryptocurrencies(client, coins_input, expected_count):
    """
    Параметризованный тест получения списка всех криптовалют
    """
    for name, pair in coins_input:
        CryptoCoin.objects.create(name=name, pair=pair)

    response = client.get("/cryptocurrencies/")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["count"] == expected_count
    assert len(data["cryptocurrencies"]) == expected_count

    returned_pairs = {coin["pair"] for coin in data["cryptocurrencies"]}
    for _, pair in coins_input:
        assert pair in returned_pairs
