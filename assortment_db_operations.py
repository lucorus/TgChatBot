import uuid

import user_db_operations as UsOper 
from base import create_connect


async def get_inventory(user_id: int, group_id: int) -> list:
  try:
    conn = await create_connect()
    account = await UsOper.get_account(user_id, group_id)
    inventory = await conn.fetch(
    '''
    SELECT * FROM inventory_item LEFT JOIN items ON inventory_item.item = items.uuid WHERE account = $1
    ''', account[0]
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


async def buy_item(item_title: str, user_id: int, group_id: int) -> None:
  try:
    conn = await create_connect()
    item = await conn.fetch("SELECT * FROM items WHERE title = $1", item_title)
    item = item[0]
    account = await UsOper.get_account(user_id, group_id)
    if item and account:
      await conn.execute(
      "INSERT INTO inventory_item (uuid, account, item) VALUES($1, $2, $3)",
      str(uuid.uuid4()), account[0], item[0])
      await conn.execute(
        "UPDATE accounts SET points = points - $1 + $2, payment = payment + $3 WHERE uuid = $4",
        item[6], item[4], item[3], account[0]
      )
    else:
      raise Exception("Объекты не найдены")
  except Exception as ex:
    print(ex, "__buy item")
