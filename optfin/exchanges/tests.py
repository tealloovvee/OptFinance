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


@pytest.mark.django_db
def test_get_exchange_by_id(client):
    """Тест получения одной биржи по ID"""
    exchange = Exchange.objects.create(
        name="Binance",
        trading_volume=Decimal("1234567890.1234567890"),
        coins_listed=350,
        rating=Decimal("9.8")
    )

    response = client.get(f"/exchanges/{exchange.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exchange.id
    assert data["name"] == "Binance"
    assert data["trading_volume"] == "1234567890.1234567890"
    assert data["coins_listed"] == 350
    assert data["rating"] == "9.80"


@pytest.mark.django_db
def test_get_exchange_not_found(client):
    """Тест получения несуществующей биржи"""
    response = client.get("/exchanges/99999/")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.parametrize(
    "exchange_id,expected_status",
    [
        (1, 200),
        (0, 404),  # Граничное значение - несуществующий ID 0
        (-1, 404),  # Отрицательный ID
        (999999, 404),  # Очень большой ID
    ],
)
@pytest.mark.django_db
def test_get_exchange_boundary_values(client, exchange_id, expected_status):
    """Параметризованный тест граничных значений для ID"""
    if expected_status == 200:
        exchange = Exchange.objects.create(
            name="Test Exchange",
            trading_volume=Decimal("1000.0"),
            coins_listed=10,
            rating=Decimal("5.0")
        )
        exchange_id = exchange.id

    response = client.get(f"/exchanges/{exchange_id}/")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name,trading_volume,coins_listed,rating,should_create",
    [
        ("A", Decimal("0.0"), 0, Decimal("0.00"), True),  # Минимальные значения
        ("B" * 100, Decimal("99999999999999999999999999.9999999999"), 2147483647, Decimal("99.99"), True),
        # Максимальные значения
        ("", Decimal("1000.0"), 10, Decimal("5.0"), False),  # Пустое имя
        ("Binance", Decimal("-1.0"), 10, Decimal("5.0"), True),  # Отрицательный volume (допустимо)
        ("Binance", Decimal("1000.0"), -1, Decimal("5.0"), True),  # Отрицательное количество монет (допустимо)
        ("Binance", Decimal("1000.0"), 10, Decimal("-1.0"), True),  # Отрицательный рейтинг (допустимо)
    ],
)
@pytest.mark.django_db
def test_exchange_boundary_values_model(client, name, trading_volume, coins_listed, rating, should_create):
    """Тест граничных значений для полей модели Exchange"""
    if should_create:
        try:
            exchange = Exchange.objects.create(
                name=name,
                trading_volume=trading_volume,
                coins_listed=coins_listed,
                rating=rating
            )
            assert exchange.name == name
        except Exception as e:
            if name == "":
                assert True
            else:
                pytest.fail(f"Should create exchange but got error: {e}")
    else:
        with pytest.raises(Exception):
            Exchange.objects.create(
                name=name,
                trading_volume=trading_volume,
                coins_listed=coins_listed,
                rating=rating
            )


@pytest.mark.django_db
def test_exchange_decimal_precision(client):
    """Тест точности Decimal полей"""
    exchange = Exchange.objects.create(
        name="Precision Test",
        trading_volume=Decimal("1234567890.1234567890"),
        coins_listed=100,
        rating=Decimal("9.87")
    )

    assert exchange.trading_volume == Decimal("1234567890.1234567890")
    assert exchange.rating == Decimal("9.87")


@pytest.mark.django_db
def test_exchange_str_representation():
    """Тест строкового представления модели"""
    exchange = Exchange.objects.create(
        name="Binance",
        trading_volume=Decimal("1000.0"),
        coins_listed=100,
        rating=Decimal("5.0")
    )
    assert str(exchange) == "Binance"
