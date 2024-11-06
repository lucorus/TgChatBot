from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
from base import dp, bot, download_file
import config


@dp.message(Command("info"))
@UsOper.public
async def user(message: Message):
  if message.reply_to_message:
    if message.reply_to_message.from_user.is_bot:
      await message.reply("Нельзя посмотреть характеристики бота!")
      return
    user = message.reply_to_message.from_user
  else:
    user = message.from_user
  user_info = await UsOper.get_account(user.id, message.chat.id)
  user_info = f'''\nДанные пользователя @{user.username} на сервере "{message.chat.title}"
  Баллы: {user_info[1]}
  Последняя активность: {user_info[2]}
  Опыт: {user_info[4]}
  Плата за сообщение: {user_info[3]}
  '''
  await message.reply(user_info)


@dp.message(Command("GetAdminStatus"))
@UsOper.private
async def get_admin_status(message: Message):
  code = message.text.split()[1]
  await message.delete()
  if code == config.AdminCode:
    await UsOper.give_admin(message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id, text="Вы получили статус администратора!")


@dp.message(Command("update_profile"))
async def update_user(message: Message):
  try:
    user_info = {
      "id": message.from_user.id,
      "first_name": message.from_user.first_name,
      "last_name": message.from_user.last_name,
    }

    await UsOper.update_user(user_info)
    return message.reply("Профиль успешно обновлён")
  except Exception as ex:
    print(ex, "__update_user")
