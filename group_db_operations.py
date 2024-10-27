from base import create_connect


async def create_group(group_info: dict) -> None:
    try:
        conn = await create_connect()
        await conn.execute(
            '''
            INSERT INTO groups (id, avatar, title) VALUES($1, $2, $3)
            ''', group_info["id"], group_info["avatar"], group_info["title"]
        )
    except Exception as ex:
        print(ex, "__create_group")


async def update_group(group_info: dict) -> None:
    try:
        conn = await create_connect()
        await conn.execute(
            '''
            UPDATE groups SET avatar = $1, title = $2 WHERE id = $3
            ''', group_info["avatar"], group_info["title"], group_info["id"]
        )
    except Exception as ex:
        print(ex, "__update_group")
        

async def get_group(group_id: int) -> list:
    try:
      conn = await create_connect()
      group = await conn.fetch("SELECT * FROM groups WHERE id = $1", group_id)
      group = group[0]
      return group
    except Exception as ex:
        print(ex, "___create_user")
        return ex
