from config import *

import psycopg2


try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    cursor = connection.cursor()
    connection.autocommit = True

    cursor.execute("DROP TABLE rarities CASCADE")
    cursor.execute("DROP TABLE items CASCADE")

    # is_admin - является ли юзер админом бота
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        avatar BYTEA,
        created_at TEXT,
        is_admin BOOL DEFAULT False
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS groups (
        id BIGINT PRIMARY KEY,
        avatar BYTEA,
        title TEXT
        )
        '''
    )

    # таблица, которая будет сохранять данные пользователя для данной группы 
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS accounts (
        uuid TEXT PRIMARY KEY,
        points BIGINT DEFAULT 1,
        last_message_time TEXT,
        payment BIGINT DEFAULT 1,
        exp BIGINT DEFAULT 1,
        "group" BIGINT REFERENCES groups(id),
        "user" BIGINT REFERENCES users(id),
        CONSTRAINT unique_group_user UNIQUE ("group", "user")
        )
        '''
    )

    # отображает редкость предмета
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS rarities (
        id SERIAL PRIMARY KEY,
        title TEXT UNIQUE,
        color TEXT UNIQUE
        )
        '''
    )

    # предмет, который может купить пользователь для увеличения характеристик / просто на память
    # если sale_price != purchase_price => на item есть скидка
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS items (
        uuid TEXT PRIMARY KEY,
        title TEXT UNIQUE,
        rarity INT REFERENCES rarities(id),
        change_payment INT,
        change_points INT,
        purchase_price INT,
        sale_price INT,
        description TEXT,
        for_sale BOOL DEFAULT True
        )
        '''
    )

    # элемент инвентаря пользователя, который отображает, что данный предмет принадлежит ему
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS inventory_item (
        uuid TEXT PRIMARY KEY,
        account TEXT REFERENCES accounts(uuid),
        item TEXT REFERENCES items(uuid)
        )
        '''
    )

except Exception as ex:
    print('POSTGRESQL ', ex)

print("success!")
