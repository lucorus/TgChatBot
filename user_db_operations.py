import datetime
import uuid

from aiogram.types import Message
from base import create_connect, time_now
import config


def admin_required(func, *args, **kwargs):
    async def wrapper(message: Message):
        user = await get_user(message.from_user.id)
        if not user[5]:
            return
        return await func(message, *args, **kwargs)
    return wrapper


def private(func,*args, **kwargs):
    async def wrapper(message: Message):
        if message.chat.type == 'private':
            return await func(message, *args, **kwargs)
        return
    return wrapper


def public(func, *args, **kwargs):
    async def wrapper(message: Message):
        if message.chat.type in ['group', 'supergroup']:
            return await func(message, *args, **kwargs)
        return
    return wrapper



async def create_user(user_info: dict) -> None:
    try:
      conn = await create_connect()
      await conn.execute(
          '''
          INSERT INTO users (id, first_name, last_name, created_at, is_admin, avatar)
          VALUES($1, $2, $3, $4, $5, $6) ON CONFLICT (id) DO NOTHING
          ''', user_info["id"], user_info["first_name"],
          user_info["last_name"], user_info["created_at"], user_info["is_admin"], user_info["avatar"]
      )
    except Exception as ex:
        print(ex, "___create_user")
        return ex


async def create_group(group_info: dict) -> None:
    try:
        conn = await create_connect()
        await conn.execute(
            '''
            INSERT INTO groups (id, avatar, title) VALUES($1, $2, $3)
            ''', group_info["id"], group_info["avatar"], group_info["title"]
        )
        print("success!")
    except Exception as ex:
        print(ex, "__create_group")


async def create_account(user_info: dict, group_info: dict, account_info: dict) -> None:
    try:
        conn = await create_connect()
        async with conn.transaction():
            # Проверка наличия пользователя
            user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', account_info["user_id"])
            if not user:
                await create_user(user_info)

            # Проверка наличия группы
            group = await conn.fetchrow('SELECT * FROM groups WHERE id = $1', account_info["group_id"])
            if not group:
                await create_group(group_info)

            # Создание аккаунта
            await conn.execute(
                '''
                INSERT INTO accounts (uuid, last_message_time, "group", "user")
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (uuid) DO NOTHING
                ''', str(uuid.uuid4()), account_info["last_message_time"], account_info["group_id"], account_info["user_id"]
            )
    except Exception as ex:
        print(ex, type(ex), "__create_account")


# функция проверяет может ли пользователь получить баллы (баллы можно получить раз в PointsCooldown)
async def can_get_points(user_id: int, group_id: int) -> bool:
    try: 
        conn = await create_connect()
        account = await conn.fetch('SELECT * FROM accounts WHERE "group"=$1 AND "user"=$2', group_id, user_id)
        account = account[0]
        if not account:
            raise IndexError("account not exists")

        time_difference = datetime.datetime.strptime(time_now(), '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
            str(account[2]), '%Y-%m-%d %H:%M:%S')

        if time_difference.total_seconds() >= config.PointsCooldown:
            return True
        return False
    except IndexError:
        raise IndexError("account not exists")
    except Exception as ex:
        print(ex, "__can_get_points")
        return False


async def add_points(user_id: int, group_id: int, points: int, last_message_time: str, const_points_count: bool = False) -> bool:
    try:
        conn = await create_connect()
        account = await conn.fetch('SELECT * FROM accounts WHERE "group"=$1 AND "user"=$2', group_id, user_id)
        if not account:
            raise IndexError("account not exists")
        
        if const_points_count:
            await conn.execute(
                '''
                UPDATE accounts SET points = points + $1, last_message_time = $2 WHERE uuid = $3
                ''', points, last_message_time, account[0][0]
            )
        else:
            await conn.execute(
                '''
                UPDATE accounts SET points = points + payment + $1, exp = exp + 1, last_message_time = $2 WHERE uuid = $3
                ''', points, last_message_time, account[0][0]
            )
        return True
    except Exception as ex:
        print(ex, type(ex), "__add_points")
        return False


async def get_user(user_id: int) -> list:
    try:
        conn = await create_connect()
        user = await conn.fetch("SELECT * FROM users WHERE id = $1", user_id)
        user = user[0]
        return user
    except Exception as ex:
        print(ex, "__get_user")
        return ex


async def get_account(user_id: int, group_id: int) -> list:
    try:
        conn = await create_connect()
        user = await conn.fetch('SELECT * FROM accounts WHERE "user" = $1 AND "group" = $2', user_id, group_id)
        user = user[0]
        return user
    except Exception as ex:
        print(ex, "__get_account")
        return ex


# выдаёт пользователю с переданным id права администратора бота
async def give_admin(user_id: int) -> None:
    try:
        conn = await create_connect()
        await conn.execute("UPDATE users SET is_admin = True WHERE id = $1", user_id)
    except Exception as ex:
        print(ex, "__give_admin")
