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


@pytest.mark.django_db
def test_get_all_cryptocurrencies_empty(client):
    """Проверка, что при отсутствии криптовалют возвращается пустой список"""
    response = client.get("/cryptocurrencies/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["count"] == 0
    assert data["cryptocurrencies"] == []


@pytest.mark.django_db
def test_get_crypto_coin_by_id(client):
    """Тест получения одной криптовалюты по ID"""
    coin = CryptoCoin.objects.create(name="Bitcoin", pair="BTC/USD")

    response = client.get(f"/cryptocurrencies/{coin.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == coin.id
    assert data["name"] == "Bitcoin"
    assert data["pair"] == "BTC/USD"


@pytest.mark.django_db
def test_get_crypto_coin_not_found(client):
    """Тест получения несуществующей криптовалюты"""
    response = client.get("/cryptocurrencies/99999/")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.parametrize(
    "coin_id,expected_status",
    [
        (1, 200),
        (0, 404),  # Граничное значение - несуществующий ID 0
        (-1, 404),  # Отрицательный ID
        (999999, 404),  # Очень большой ID
    ],
)
@pytest.mark.django_db
def test_get_crypto_coin_boundary_values(client, coin_id, expected_status):
    """Параметризованный тест граничных значений для ID"""
    if expected_status == 200:
        coin = CryptoCoin.objects.create(name="Test", pair="TEST/USD")
        coin_id = coin.id

    response = client.get(f"/cryptocurrencies/{coin_id}/")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name,pair,should_create",
    [
        ("A", "A/USD", True),  # Минимальная длина
        ("B" * 100, "BTC/USD", True),  # Максимальная длина для name
        ("Bitcoin", "A" * 50, True),  # Максимальная длина для pair
        ("", "BTC/USD", False),  # Пустое имя
        ("Bitcoin", "", False),  # Пустая пара
    ],
)
@pytest.mark.django_db
def test_crypto_coin_boundary_values_model(client, name, pair, should_create):
    """Тест граничных значений для полей модели"""
    if should_create:
        try:
            coin = CryptoCoin.objects.create(name=name, pair=pair)
            assert coin.name == name
            assert coin.pair == pair
        except Exception as e:
            pytest.fail(f"Should create coin but got error: {e}")
    else:
        with pytest.raises(Exception):
            CryptoCoin.objects.create(name=name, pair=pair)


@pytest.mark.django_db
def test_crypto_coin_unique_pair(client):
    """Тест уникальности пары криптовалют"""
    CryptoCoin.objects.create(name="Bitcoin", pair="BTC/USD")

    with pytest.raises(Exception):  # IntegrityError или ValidationError
        CryptoCoin.objects.create(name="Bitcoin Cash", pair="BTC/USD")


@pytest.mark.django_db
def test_crypto_coin_str_representation():
    """Тест строкового представления модели"""
    coin = CryptoCoin.objects.create(name="Bitcoin", pair="BTC/USD")
    assert str(coin) == "BTC/USD"