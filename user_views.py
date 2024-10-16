from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
from base import dp, bot


@dp.message(Command("info"))
async def user(message: Message):
  user_info = await UsOper.get_account(message.from_user.id, message.chat.id)
  user_info = f'''\nВаши данные на сервере "{message.chat.title}"
  Баллы: {user_info[1]}
  Последняя активность: {user_info[2]}
  Опыт: {user_info[4]}
  Плата за сообщение: {user_info[3]}
  '''

  await message.delete()
  await bot.send_message(chat_id=message.from_user.id, text=user_info)
