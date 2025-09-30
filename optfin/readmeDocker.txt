Прописать в .env.docker:
1) название бд
2) юзера
3) пароль

Докер сам соберет бд и запустит ее

Для запуска проекта нужно ввести одну команду
docker compose build

Далее
docker-compose up -d

После docker compose up -d нужно:
Выполнить миграции:
docker compose exec web python manage.py migrate

(Опционально) создать суперпользователя:
docker compose exec web python manage.py createsuperuser

Зайти в админку
http://localhost:8000/admin

Django будет доступен на http://localhost:8000
PostgreSQL на localhost:5432

Несколько полезных инструкций для контейнера:
docker-compose down       # останавливает контейнеры
docker-compose up -d      # запускает в фоновом режиме

Больше информации можно узнать командой docker в консоль с установленным докером
http://localhost:8000
