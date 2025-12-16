Инструкция для фронта

ВАЖНО: Убедитесь, что бэкенд уже запущен на http://localhost:8000

1. Сборка Docker образа:

   Если бэкенд на localhost (то же самое, где запускаете Docker):
   docker build -t my-frontend .

   Если бэкенд в Docker контейнере или на другом хосте:
   docker build --build-arg VITE_API_URL=http://localhost:8000 -t my-frontend .

   Для Windows/Mac (если бэкенд в Docker):
   docker build --build-arg VITE_API_URL=http://host.docker.internal:8000 -t my-frontend .

2. Запуск контейнера:
   docker run -p 3000:80 my-frontend

3. Открыть в браузере:
   http://localhost:3000

(nginx слушает 80, но локально мы мапим на 3000)

ПРИМЕЧАНИЕ:
- Фронтенд работает в браузере пользователя, поэтому localhost:8000 означает localhost вашего компьютера
- Если бэкенд тоже в Docker, он должен быть доступен на localhost:8000 (порт проброшен)
- CORS уже настроен для работы с localhost:3000 и localhost:5173