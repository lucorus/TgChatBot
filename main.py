import asyncio
from aiogram.types import Message
from aiogram.filters import Command

import user_db_operations as UsOper
import config
import user_views, assortment_views, group_views
from base import bot, dp, download_file, time_now


# Обработчик сообщений в группе
@dp.message()
@UsOper.public
async def handle_message(message: Message):
    if message.from_user.is_bot:
        return
    now = time_now()
    try:
        if await UsOper.can_get_points(message.from_user.id, message.chat.id):
            await UsOper.add_points(group_id=message.chat.id, user_id=message.from_user.id, points=0, last_message_time=now)
    except IndexError:
        # Собираем информацию, чтобы создать аккаунт/профиль для пользователя
        chat_info = await bot.get_chat(message.chat.id)

        user_info = {
            "id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "created_at": now,
            "is_admin": False,
        }

        group_info = {
            "id": message.chat.id,
            "title": message.chat.title,
        }

        account_info = {
            "last_message_time": str(message.date.strftime('%Y-%m-%d %H:%M:%S')),
            "user_id": message.from_user.id,
            "group_id": message.chat.id
        }
        await UsOper.create_account(user_info, group_info, account_info)
    except Exception as ex:
        print(ex, "__main_func")

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
