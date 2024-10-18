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
