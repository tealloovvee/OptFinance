from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import User
from .jwt_utils import verify_token


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        token = None
        query_string = scope.get("query_string", b"").decode()

        if query_string:
            params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
            token = params.get("token")

        if not token:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if token:
            user = await self.get_user_from_token(token)
            if user:
                scope["user"] = user
            else:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Получает пользователя из JWT токена"""
        payload = verify_token(token)
        if payload and payload.get('type') == 'access':
            try:
                return User.objects.get(id=payload['user_id'])
            except User.DoesNotExist:
                return None
        return None

