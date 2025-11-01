import asyncio
import os
import django
from aiogram import Bot, Dispatcher, types
from channels.layers import get_channel_layer

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MainProject.settings')
    django.setup()

from django.conf import settings

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
ADMIN_CHAT_ID = settings.ADMIN_CHAT_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_admin_reply(message: types.Message):
    if message.reply_to_message:
        original_text = message.reply_to_message.text
        if original_text and original_text.startswith("UserID:"):
            try:
                user_id = int(original_text.split("|")[0].replace("UserID:", "").strip())
                reply_text = message.text
                if reply_text:
                    channel_layer = get_channel_layer()
                    await channel_layer.group_send(
                        f"user_{user_id}",
                        {
                            "type": "chat.message",
                            "message": reply_text
                        }
                    )
            except (ValueError, AttributeError) as e:
                # Логируем ошибку, если не удалось обработать ответ
                print(f"Error handling admin reply: {e}")


async def send_message_to_admin(user_id: int, user_name: str, text: str):
    msg = f"UserID:{user_id} | {user_name} написал:\n{text}"
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

async def start_bot():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot())