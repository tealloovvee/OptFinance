Инструкция для фронта

1. Сборка Docker образа:
   docker build -t my-frontend .

2. Запуск контейнера:
   docker run -p 3000:80 my-frontend

3. Открыть в браузере:
   http://localhost:3000

(nginx слушает 80, но локально мы мапим на 3000)