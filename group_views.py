from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
import group_db_operations as GroupOper
from base import dp


@dp.message(Command("update_group_info"))
@UsOper.public
async def update_group(message: Message):
  try:
    group_info = {
      "id": message.chat.id,
      "title": message.chat.title,
    }
    await GroupOper.update_group(group_info)
    await message.reply("Данные группы успешно обновлены!")
  except Exception as ex:
    print(ex, "__update_group")
