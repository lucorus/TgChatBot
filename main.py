import asyncio
import logging
import sys
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import config
import user_db_operations


API_TOKEN = config.token


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def download_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


@dp.message(Command("user"))
async def user(message: Message):
    await user_db_operations.get_user(message.from_user.id)
    await message.answer("Ok!")


@dp.message(Command("users"))
async def user(message: Message):
    await user_db_operations.get_users()
    await message.answer("Ok!")


@dp.message(Command("accounts"))
async def user(message: Message):
    await user_db_operations.get_accounts()
    await message.answer("Ok!")


# Обработчик сообщений в группе
@dp.message(lambda message: message.chat.type in ['group', 'supergroup'])
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_avatar = await bot.get_user_profile_photos(user_id)
    group_id = message.chat.id
    group_avatar = await bot.get_chat(group_id)

    user_avatar_file_id = user_avatar.photos[0][-1].file_id if user_avatar.photos else None
    group_avatar_file_id = group_avatar.photo.big_file_id if group_avatar.photo else None

    user_avatar_url = None
    group_avatar_url = None

    if user_avatar_file_id:
        user_avatar_file = await bot.get_file(user_avatar_file_id)
        user_avatar_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{user_avatar_file.file_path}"

    if group_avatar_file_id:
        group_avatar_file = await bot.get_file(group_avatar_file_id)
        group_avatar_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{group_avatar_file.file_path}"


    created_at = message.date.strftime('%Y-%m-%d %H:%M:%S')

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
        "created_at": created_at,
        "is_admin": False,
        "avatar": file_data
    }

    group_info = {
        "id": message.chat.id,
        "avatar": group_avatar,
        "title": message.chat.title,
    }


    success = await user_db_operations.add_points(message.from_user.id, message.chat.id, 1, 
                                                  str(message.date.strftime('%Y-%m-%d %H:%M:%S')))
    if success == False:
        account_info = {
            "last_message_time": str(message.date.strftime('%Y-%m-%d %H:%M:%S')),
            "user_id": message.from_user.id,
            "group_id": message.chat.id
        }
        await user_db_operations.create_account(user_info, group_info, account_info)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
