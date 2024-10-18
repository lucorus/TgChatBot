import asyncio
from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
import config
import user_views
import assortment_views
from base import bot, dp, download_file


# Обработчик сообщений в группе
@dp.message(lambda message: message.chat.type in ['group', 'supergroup'])
async def handle_message(message: Message):
    if message.from_user.is_bot:
        return
    now = message.date.strftime('%Y-%m-%d %H:%M:%S')
    try:
        if await UsOper.can_get_points(message.from_user.id, message.chat.id):
            await UsOper.add_points(group_id=message.chat.id, user_id=message.from_user.id, points=1, last_message_time=now)
    except IndexError:
        # Собираем информацию, чтобы создать аккаунт/профиль для пользователя
        user_photos = await bot.get_user_profile_photos(message.from_user.id)
        chat_info = await bot.get_chat(message.chat.id)

        user_avatar_file_id = user_photos.photos[0][-1].file_id if user_photos.photos else None
        group_avatar_file_id = chat_info.photo.big_file_id if chat_info.photo else None

        user_avatar_url, group_avatar_url  = None, None

        if user_avatar_file_id:
            user_avatar_file = await bot.get_file(user_avatar_file_id)
            user_avatar_url = f"https://api.telegram.org/file/bot{config.token}/{user_avatar_file.file_path}"

        if group_avatar_file_id:
            group_avatar_file = await bot.get_file(group_avatar_file_id)
            group_avatar_url = f"https://api.telegram.org/file/bot{config.token}/{group_avatar_file.file_path}"

        file_data = None
        if user_avatar_url:
            file_data = await download_file(user_avatar_url)

        group_avatar = None
        if group_avatar_url:
            group_avatar = await download_file(group_avatar_url)

        user_info = {
            "id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "created_at": now,
            "is_admin": False,
            "avatar": file_data
        }

        group_info = {
            "id": message.chat.id,
            "avatar": group_avatar,
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
