from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
import group_db_operations as GroupOper
from base import dp, bot, download_file
import config


@dp.message(Command("update_group_info"))
@UsOper.public
async def update_group(message: Message):
  try:
    chat_info = await bot.get_chat(message.chat.id)
    group_avatar_file_id = chat_info.photo.big_file_id if chat_info.photo else None
    group_avatar_url  = None

    if group_avatar_file_id:
      group_avatar_file = await bot.get_file(group_avatar_file_id)
      group_avatar_url = f"https://api.telegram.org/file/bot{config.token}/{group_avatar_file.file_path}"

    group_avatar = None
    if group_avatar_url:
      group_avatar = await download_file(group_avatar_url)

    group_info = {
      "id": message.chat.id,
      "avatar": group_avatar,
      "title": message.chat.title,
    }
    await GroupOper.update_group(group_info)
    await message.reply("Данные группы успешно обновлены!")
  except Exception as ex:
    print(ex, "__update_group")
