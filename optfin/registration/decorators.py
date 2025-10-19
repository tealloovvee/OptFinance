from functools import wraps
from django.http import JsonResponse
from .jwt_utils import verify_token


def jwt_required(view_func):
    """
    Декоратор для защиты эндпоинтов JWT токеном
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Missing or invalid authorization header'}, status=401)

        token = auth_header.split(' ')[1]

        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)

        request.user_id = payload['user_id']
        request.user_login = payload['login']
        request.user_email = payload['email']
        request.user_role = payload['role']

        return view_func(request, *args, **kwargs)

    return wrapper
