import uuid

import user_db_operations as UsOper 
from base import create_connect
from utils import UserInputException
import config


async def get_inventory(user_id: int, group_id: int, page: int = 0) -> list:
  try:
    conn = await create_connect()
    account = await UsOper.get_account(user_id, group_id)
    inventory = await conn.fetch(
    '''
    SELECT * FROM inventory_item LEFT JOIN items ON inventory_item.item = items.uuid WHERE account = $1 LIMIT $2 OFFSET $3
    ''', account[0], config.PageSize, page * config.PageSize
    )
    return inventory
  except Exception as ex:
    print(ex, "___get_inventory")
    return ex
    

async def get_assortment() -> list:
  try:
    conn = await create_connect()
    assortment = await conn.fetch("SELECT * FROM items LEFT JOIN rarities ON items.rarity = rarities.id WHERE for_sale = True")
    return assortment
  except Exception as ex:
    print(ex, "___get_inventory")
    return ex
    

async def get_rarities() -> list:
  try:
    conn = await create_connect()
    rarities = await conn.fetch("SELECT * FROM rarities")
    return rarities
  except Exception as ex:
    print(ex, "___get_rarities")
    return ex
  

async def create_rarity(title: str, color: str) -> None:
  try:
    conn = await create_connect()
    await conn.execute("INSERT INTO rarities (title, color) VALUES($1, $2)", title, color)
  except Exception as ex:
    print(ex, "__create_rarity")


async def create_item(item_info: dict) -> None:
  try:
    conn = await create_connect()
    await conn.execute(
      '''
      INSERT INTO items (uuid, title, rarity, change_payment, change_points, purchase_price, sale_price, description) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
      ''', str(uuid.uuid4()), item_info["title"], item_info["rarity"], item_info["change_payment"],item_info["change_points"],
      item_info["purchase_price"], item_info["sale_price"], item_info["description"]
    )
  except Exception as ex:
    print(ex, "__create_item")


async def delete_item(title: str) -> bool:
  try:
    conn = await create_connect()
    await conn.execute("DELETE FROM items CASCADE WHERE title = $1", title)
    return True
  except Exception as ex:
    print(ex, "__delete_item")
    return False


async def delete_rarity(title: str) -> bool:
  try:
    conn = await create_connect()
    await conn.execute("DELETE FROM rarities CASCADE WHERE title = $1", title)
    return True
  except Exception as ex:
    print(ex, "__delete_rarity")
    return False


async def update_rarity(old_title: str, title: str, color: str) -> None:
  try:
    conn = await create_connect()
    await conn.execute("UPDATE rarities SET title = $1, color = $2 WHERE title = $3", title, color, old_title)
  except Exception as ex:
    print(ex, "__update_rarity")


async def update_item(item_info: dict) -> None:
  try:
    conn = await create_connect()
    await conn.execute(
      '''
      UPDATE items SET title = $1, rarity = $2, change_payment = $3, change_points = $4, purchase_price = $5, sale_price = $6, description = $7 WHERE title = $8
      ''', item_info["title"], item_info["rarity"], item_info["change_payment"],item_info["change_points"],
      item_info["purchase_price"], item_info["sale_price"], item_info["description"], item_info["old_title"]
    )
  except Exception as ex:
    print(ex, "__update_item")


# user1 - пользователь, который покупает предмет, user2 - тот, кому покупают предмет (может быть одним юзером)
async def buy_item(item_title: str, user1_id: int, user2_id: int, group_id: int) -> None:
  try:
    conn = await create_connect()
    item = await conn.fetch("SELECT * FROM items WHERE title = $1", item_title)
    if item:
      item = item[0]
      account1 = await UsOper.get_account(user1_id, group_id)
      if account1:
        # получаем значение для второго юзера, если он не равен первому юзеру
        account2 = await UsOper.get_account(user2_id, group_id) if user1_id != user2_id else account1
        if account2:
          await conn.execute(
          "INSERT INTO inventory_item (uuid, account, item) VALUES($1, $2, $3)",
          str(uuid.uuid4()), account2[0], item[0])

          # устанавливаем значения для переменных, которые будут показывать изменение
          # характеристик для человека, купившего предмет (user1), и для того, которому 
          # покупают (user2)
          if item[3] < 0:
            dif_payment_1 = item[3]
            dif_payment_2 = 0
          else:
            dif_payment_1 = 0
            dif_payment_2 = item[3]


          if item[4] < 0:
            dif_points_1 = item[4]
            dif_points_2 = 0
          else:
            dif_points_1 = 0
            dif_points_2 = item[4]

          if account1[1] - dif_points_1 - item[6] < 0 or account1[3] - dif_points_2 <= 0:
            raise UserInputException("Недостаточно характеристик для покупки данного предмета")

          async with conn.transaction():
          # бонусы после добавления предмета
            await conn.execute(
              "UPDATE accounts SET points = points + $1, payment = payment + $2 WHERE uuid = $3",
              dif_points_2, dif_payment_2, account2[0]
            )
            # сама покупка предмета
            await conn.execute(
              "UPDATE accounts SET points = points + $1, payment = payment + $2 WHERE uuid = $3", 
              (dif_points_1 - item[6]), dif_payment_1, account1[0])
        else:
          raise UserInputException("Информация о пользователе, которому покупают предмет не найдена")
      else:
        raise UserInputException("Информация о покупателе не найдена")
    else:
      raise UserInputException("Предмет не найден")
  except Exception as ex:
    print(ex, "__buy item")
