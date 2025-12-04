import asyncio
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from telegramBot.bot import send_message_to_admin
from registration.decorators import jwt_required

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")

@api_view(['POST'])
@jwt_required
def send_message(request):
    try:
        data = request.data
        text = data.get("message")
        if not text:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(send_message_to_admin(user.id, user.login, text))
                    )
                    future.result(timeout=5)
            else:
                loop.run_until_complete(send_message_to_admin(user.id, user.login, text))
        except RuntimeError:
            asyncio.run(send_message_to_admin(user.id, user.login, text))

        return Response({"status": "ok"})
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return Response({"error": "Failed to send message"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)