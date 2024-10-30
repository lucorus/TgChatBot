from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot

import user_db_operations as UsOper
import assortment_db_operations as AssortOper
from base import dp, bot
from utils import UserInputException


@dp.message(Command("inventory"))
@UsOper.public
async def get_inventory(message: Message):
  inventory = await AssortOper.get_inventory(message.from_user.id, message.chat.id)
  if inventory:
    inventory_list = f'Ваш инвентарь на сервере {message.chat.title}:'
    for item in inventory:
      inventory_list += f'''
        \n{item[4]} ({item[5]}):
 Изменение оплаты: {item[6]}
 Изменение количества баллов: {item[7]}
 Цена: {item[9]}
 Описание: {item[10]}
 Возможно купить: {"True" if item[10] else "False"}
        '''
    await message.reply(inventory_list)
  

@dp.message(Command("assortment"))
async def assortment(message: Message):
  try:
    assortment = await AssortOper.get_assortment()
    if assortment:
      assortment_list = f'Ассортимент:'
      for item in assortment:
        assortment_list += f'''
        \n{item[1]} ({item[10]}):
 Изменение оплаты: {item[3]}
 Изменение количества баллов: {item[4]}
 Цена: {item[6]}
 Описание: {item[7]}
        '''
      await message.reply(assortment_list)
  except Exception as ex:
    print(ex, "__get_assortment")


@dp.message(Command("rarities"))
async def rarities(message: Message):
  try:
    rarities = await AssortOper.get_rarities()
    if rarities:
      rarities_list = f'Редкости:\n'
      for item in rarities:
        rarities_list += f"{item[0]} - {item[1]}"
      await bot.send_message(chat_id=message.from_user.id, text=rarities_list)
  except Exception as ex:
    print(ex, "__rarities")


@dp.message(Command("CreateRarity"))
@UsOper.admin_required
async def create_rarity(message: Message):
  try:
    await message.delete()
    message_text = message.text.split()
    title, color = message_text[1], message_text[2]
    await AssortOper.create_rarity(title, color)
    await bot.send_message(chat_id=message.from_user.id, text=f'Редкость "{title}" создана')
  except Exception as ex:
    print(ex, "__create_rarity")


@dp.message(Command("CreateItem"))
@UsOper.admin_required
async def create_item(message: Message):
  try:
    await message.delete()
    message_text = message.text.split()

    if len(message_text) < 7:
      await bot.send_message(chat_id=message.from_user.id, text=f'Недостаточно данных')
    elif len(message_text) == 7: # делаем описание к предмету пустым
      message_text[7] = ""

    item_info = {
      "title": message_text[1],
      "rarity": int(message_text[2]),
      "change_payment": int(message_text[3]),
      "change_points": int(message_text[4]),
      "purchase_price": int(message_text[5]),
      "sale_price": int(message_text[6]),
      "description": ''.join(message_text[7:]),
    }
    await AssortOper.create_item(item_info)
    await bot.send_message(chat_id=message.from_user.id, text=f'Предмет {item_info["title"]} создан!')
  except Exception as ex:
    print(ex, "__create_item")


@dp.message(Command("DeleteItem"))
@UsOper.admin_required
async def delete_item(message: Message):
  try:
    await message.delete()
    title = message.text.split()[1]
    success = await AssortOper.delete_item(title)
    if success:
      await bot.send_message(chat_id=message.from_user.id, text=f"Предмет {title} удалён")
    else:
      await bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка")
  except Exception as ex:
    print(ex, "__delete_item")


@dp.message(Command("DeleteRarity"))
@UsOper.admin_required
async def delete_rarity(message: Message):
  try:
    await message.delete()
    title = message.text.split()[1]
    success = await AssortOper.delete_rarity(title)
    if success:
      await bot.send_message(chat_id=message.from_user.id, text=f"Редкость {title} удалена")
    else:
      await bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка")
  except Exception as ex:
    print(ex, "__delete_rarity")


@dp.message(Command("UpdateItem"))
@UsOper.admin_required
async def update_item(message: Message):
  try:
    await message.delete()
    message_text = message.text.split()

    if len(message_text) < 8:
      await bot.send_message(chat_id=message.from_user.id, text=f'Недостаточно данных')
    elif len(message_text) == 8: # делаем описание к предмету пустым
      message_text[8] = ""

    item_info = {
      "old_title": message_text[1],
      "title": message_text[2],
      "rarity": int(message_text[3]),
      "change_payment": int(message_text[4]),
      "change_points": int(message_text[5]),
      "purchase_price": int(message_text[6]),
      "sale_price": int(message_text[7]),
      "description": ' '.join(message_text[8:]),
    }
    await AssortOper.update_item(item_info)
    await bot.send_message(chat_id=message.from_user.id, text=f'Предмет {item_info["title"]} обновлён!')
  except Exception as ex:
    print(ex, "__update_item")


@dp.message(Command("UpdateRarity"))
@UsOper.admin_required
async def update_rarity(message: Message):
  try:
    await message.delete()
    message_text = message.text.split()
    old_title, title, color = message_text[1], message_text[2], message_text[3]
    await AssortOper.update_rarity(old_title, title, color)
    await bot.send_message(chat_id=message.from_user.id, text=f'Редкость "{title}" обновлена')
  except Exception as ex:
    print(ex, "__update_rarity")


@dp.message(Command("buy"))
@UsOper.public
async def buy_item(message: Message):
  try:
    text_words = message.text.split()
    if message.reply_to_message:
      user_id = message.reply_to_message.from_user.id
    else:
      user_id = message.from_user.id
    item_title = text_words[1]
                
    await AssortOper.buy_item(item_title, message.from_user.id, user_id, message.chat.id)
    await message.reply(f"Предмет {item_title} куплен!")
  except UserInputException as ex:
    await message.reply(ex.message)
  except Exception as ex:
    print(ex, "__buy_item")