# Инструкция по запуску скрапера CoinGecko

## Описание

Микросервис `coingeckoScrapper` предназначен для автоматического заполнения базы данных информацией о криптовалютах и их исторических данных OHLCV (Open, High, Low, Close, Volume) из API CoinGecko.

## Что делает скрапер

1. **Заполнение таблицы криптовалют** (`CryptoCoin`):
   - Если таблица пуста, загружает топ-30 криптовалют по рыночной капитализации
   - Сохраняет название монеты и торговую пару (например, BTC/USDT)

2. **Загрузка исторических данных OHLCV** (`OHLCV`):
   - Для каждой криптовалюты загружает свечные данные за последний день
   - Сохраняет данные: timestamp, open, high, low, close, volume
   - Интервал: 1 день

## Структура проекта

```
optfin/
├── coingeckoScrapper/
│   ├── __init__.py
│   └── main.py              # Основной файл скрапера
├── coingecko_scraper_cron   # Cron конфигурация (запуск каждый час)
├── cryptocurrencies/
│   └── models.py            # Модель CryptoCoin
├── modelsMark/
│   └── models.py            # Модель OHLCV
└── MainProject/
    └── settings.py          # Настройки Django
```

## Требования

- Python 3.13+
- Django 5.2.6+
- PostgreSQL база данных
- Установленные зависимости из `requirements.txt`
- API ключ CoinGecko (уже указан в коде: `CG-tpMDjB6SNKH7F3QWuRpsUrXY`)
- Настроенный файл `.env` с параметрами подключения к БД

## Настройка окружения

### 1. Переменные окружения (.env)

Убедитесь, что файл `.env` содержит следующие переменные:

```env
DB_NAME=optfindb
DB_USER=Nephilim
DB_PASSWORD=project7162wkfgmk
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
```

### 2. Настройка Django

Скрипт автоматически настраивает Django окружение:
- Добавляет путь к проекту в `sys.path`
- Устанавливает `DJANGO_SETTINGS_MODULE`
- Инициализирует Django через `django.setup()`

## Способы запуска скрапера

### Способ 1: Запуск вручную (локально)

#### Шаг 1: Активация виртуального окружения (если используется)

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Шаг 2: Установка зависимостей

```bash
pip install -r requirements.txt
```

#### Шаг 3: Настройка базы данных

Убедитесь, что:
- PostgreSQL запущен и доступен
- База данных создана
- Миграции применены:

```bash
python manage.py migrate
```

#### Шаг 4: Запуск скрапера

Из корневой директории проекта `optfin/`:

```bash
python coingeckoScrapper/main.py
```

Или с указанием полного пути:

```bash
python -m coingeckoScrapper.main
```

### Способ 2: Запуск через Docker

#### Шаг 1: Запуск контейнеров

```bash
docker compose build
docker compose up -d
```

#### Шаг 2: Применение миграций (если еще не применены)

```bash
docker compose exec web python manage.py migrate
```

#### Шаг 3: Запуск скрапера в контейнере

```bash
docker compose exec web python coingeckoScrapper/main.py
```

### Способ 3: Автоматический запуск через Cron (Docker)

Скрапер настроен на автоматический запуск каждый час через cron.

#### Настройка cron (уже выполнено в Dockerfile):

Файл `coingecko_scraper_cron` содержит:
```
0 * * * * root cd /codefile && /usr/local/bin/python coingeckoScrapper/main.py >> /var/log/coingecko_scraper.log 2>&1
```

Это означает:
- Запуск каждый час (в 0 минут каждого часа)
- Логирование в `/var/log/coingecko_scraper.log`

#### Проверка логов cron:

```bash
docker compose exec web tail -f /var/log/coingecko_scraper.log
```

#### Ручной запуск cron задачи:

```bash
docker compose exec web bash -c "cd /codefile && python coingeckoScrapper/main.py"
```

## Проверка результатов

### 1. Проверка через Django shell

```bash
# Локально
python manage.py shell

# В Docker
docker compose exec web python manage.py shell
```

В shell:

```python
from cryptocurrencies.models import CryptoCoin
from modelsMark.models import OHLCV

# Проверка количества криптовалют
print(f"Криптовалют в БД: {CryptoCoin.objects.count()}")

# Проверка данных OHLCV
print(f"Записей OHLCV в БД: {OHLCV.objects.count()}")

# Просмотр последних записей
for coin in CryptoCoin.objects.all()[:5]:
    ohlcv_count = OHLCV.objects.filter(trading_pair=coin).count()
    print(f"{coin.pair}: {ohlcv_count} записей OHLCV")
```

### 2. Проверка через Django Admin

1. Откройте http://localhost:8000/admin
2. Войдите с учетными данными суперпользователя
3. Проверьте разделы:
   - **Cryptocurrencies** → **Crypto coins**
   - **Models mark** → **OHLCVs**

### 3. Проверка через API

```bash
# Получить список криптовалют
curl http://localhost:8000/cryptocurrencies/

# Получить список бирж (если заполнены)
curl http://localhost:8000/exchanges/
```

## Ограничения и особенности

### Rate Limiting

Скрапер использует декораторы для ограничения частоты запросов:
- `fill_crypto_table_if_empty`: максимум 20 запросов в минуту
- `fetch_ohlcv`: максимум 10 запросов в минуту

Это необходимо для соблюдения лимитов API CoinGecko.

### Первый запуск

При первом запуске скрапер:
1. Проверяет, есть ли данные в таблице `CryptoCoin`
2. Если таблица пуста, загружает топ-30 криптовалют
3. Для каждой криптовалюты загружает OHLCV данные

### Последующие запуски

При повторных запусках:
- Криптовалюты не добавляются повторно (если таблица не пуста)
- OHLCV данные обновляются через `update_or_create` (обновляются существующие записи)

## Устранение проблем

### Ошибка: "No module named 'django'"

**Решение**: Установите зависимости:
```bash
pip install -r requirements.txt
```

### Ошибка подключения к БД

**Решение**: Проверьте:
1. PostgreSQL запущен
2. Параметры в `.env` корректны
3. База данных создана
4. Миграции применены

### Ошибка: "request error CoinGecko: 429"

**Решение**: Превышен лимит запросов к API. Подождите несколько минут и повторите запуск.

### Ошибка: "table is already filled"

**Решение**: Это не ошибка. Сообщение означает, что таблица криптовалют уже содержит данные. Скрипт продолжит работу и обновит OHLCV данные.

### Проверка логов

Логи Django находятся в папке `logs/`:
- `debug.log` - отладочная информация
- `info.log` - информационные сообщения
- `error.log` - ошибки

## Дополнительная информация

### Изменение количества загружаемых криптовалют

В файле `coingeckoScrapper/main.py` измените параметр `limit`:

```python
fill_crypto_table_if_empty(limit=50)  # Вместо 30 по умолчанию
```

### Изменение интервала данных OHLCV

В функции `main()` измените параметр `interval`:

```python
ohlcv = fetch_ohlcv(coin.name, "7")  # 7 дней вместо 1
```

Доступные значения: `"1"`, `"7"`, `"14"`, `"30"`, `"90"`, `"180"`, `"365"`

### Ручной запуск для конкретной криптовалюты

Можно модифицировать скрипт для загрузки данных конкретной монеты:

```python
from cryptocurrencies.models import CryptoCoin

coin = CryptoCoin.objects.get(name="bitcoin")
ohlcv = fetch_ohlcv(coin.name, "1")
if ohlcv:
    save_ohlcv(coin, ohlcv, "1")
```

## Контакты и поддержка

При возникновении проблем проверьте:
1. Логи Django в папке `logs/`
2. Логи cron (в Docker): `/var/log/coingecko_scraper.log`
3. Статус контейнеров: `docker compose ps`
4. Подключение к БД: `docker compose exec db psql -U Nephilim -d optfindb`


