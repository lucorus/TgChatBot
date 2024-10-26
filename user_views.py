from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
from base import dp, bot
import config


@dp.message(Command("info"))
@UsOper.public
async def user(message: Message):
  user_info = await UsOper.get_account(message.from_user.id, message.chat.id)
  user_info = f'''\nВаши данные на сервере "{message.chat.title}"
  Баллы: {user_info[1]}
  Последняя активность: {user_info[2]}
  Опыт: {user_info[4]}
  Плата за сообщение: {user_info[3]}
  '''
  await message.reply(user_info)


@dp.message(Command("get_admin_status"))
@UsOper.private
async def get_admin_status(message: Message):
  code = message.md_text[20:]
  await message.delete()
  if code == config.AdminCode:
    await UsOper.give_admin(message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id, text="Вы получили статус администратора!")
