from base import create_connect


async def get_group(group_id: int) -> list:
    try:
      conn = await create_connect()
      group = await conn.fetch("SELECT * FROM groups WHERE id = $1", group_id)
      group = group[0]
      return group
    except Exception as ex:
        print(ex, "___create_user")
        return ex
