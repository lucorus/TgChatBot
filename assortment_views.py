from aiogram.filters import Command
from aiogram.types import Message

import user_db_operations as UsOper
import assortment_db_operations as AssortOper
from base import dp, bot


@dp.message(lambda message: message.chat.type in ['group', 'supergroup'], Command("inventory"))
async def get_inventory(message: Message):
  await message.delete()
  inventory = await AssortOper.get_inventory(message.from_user.id, message.chat.id)
  print(inventory)
  if inventory:
    inventory_list = f'Ваш инвентарь на сервере {message.chat.title}:'
    for item in inventory:
      inventory_list += f'''\n
      '''
    await bot.send_message(chat_id=message.from_user.id, text=inventory)
  

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
      await bot.send_message(chat_id=message.from_user.id, text=assortment_list)
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


@UsOper.admin_required
@dp.message(Command("CreateRarity"))
async def create_rarity(message: Message):
  try:
    await message.delete()
    message_text = message.text.split()
    title, color = message_text[1], message_text[2]
    await AssortOper.create_rarity(title, color)
    await bot.send_message(chat_id=message.from_user.id, text=f'Редкость "{title}" создана')
  except Exception as ex:
    print(ex, "__create_rarity")


@UsOper.admin_required
@dp.message(Command("CreateItem"))
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


@UsOper.admin_required
@dp.message(Command("DeleteItem"))
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


@UsOper.admin_required
@dp.message(Command("DeleteRarity"))
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
