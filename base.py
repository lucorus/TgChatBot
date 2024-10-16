import datetime
import pytz

import asyncpg
import logging
import sys
from aiogram import Bot, Dispatcher
import aiohttp

import config

timezone = pytz.timezone('Europe/Moscow')
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot = Bot(token=config.token)
dp = Dispatcher()


async def create_connect():
    try:
        conn = await asyncpg.connect(
            password=config.password,
            database=config.db_name,
            user=config.user,
            host=config.host
        )
        return conn
    except Exception as ex:
        print(ex)


async def download_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


def time_now() -> str:
    moscow_time = datetime.datetime.now(timezone)
    formatted_time = moscow_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

