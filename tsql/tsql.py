from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import time
import json
import pandas as pd
import random
import sqlite3


class TSQL:
    def __init__(
        self,
        api_id,
        api_hash,
        sessionName,
        chanellInviteLink,
        databaseStructurePath,
        encryptKey="",
    ):
        self.client = TelegramClient(sessionName, api_id, api_hash)
        self.chanellInviteLink = chanellInviteLink
        self.databaseStructurePath = databaseStructurePath
        self.encryptKey = encryptKey
        self.all_message_ids = []
        self.salt = get_random_bytes(16)

    def __get_key__(self, password):
        return PBKDF2(password, self.salt, dkLen=32)

    def __encrypt__(self, plain_text, password):
        key = self.__get_key__(password)
        cipher = AES.new(key, AES.MODE_GCM)
        nonce = cipher.nonce
        cipher_text, tag = cipher.encrypt_and_digest(plain_text.encode("utf-8"))
        return base64.b64encode(self.salt + nonce + tag + cipher_text).decode("utf-8")

    def __decrypt__(self, encrypted_text, password):
        encrypted_data = base64.b64decode(encrypted_text)
        salt_from_data = encrypted_data[:16]
        nonce = encrypted_data[16:32]
        tag = encrypted_data[32:48]
        cipher_text = encrypted_data[48:]
        key = PBKDF2(password, salt_from_data, dkLen=32)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(cipher_text, tag).decode("utf-8")

    async def __readRawDBJson__(self):
        history = await self.client(
            GetHistoryRequest(
                peer=self.channel,
                limit=1000,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0,
            )
        )
        db_raw = ""
        for message in history.messages:
            if message.message:
                self.all_message_ids.append(message.id)

                if message.message == "#init":
                    return "#init"

                db_raw += message.message

        if self.encryptKey != "" and db_raw != "":
            db_raw = self.__decrypt__(db_raw, self.encryptKey)

        return db_raw

    def __chunkString__(self, string, chunk_size=4000):
        return [string[i : i + chunk_size] for i in range(0, len(string), chunk_size)]

    async def __deleteAllMessages__(self):
        await self.__readRawDBJson__()

        if self.all_message_ids:
            await self.client.delete_messages(self.channel, self.all_message_ids)

    def __jsonToSqlite__(self, json_data):
        self.data = json.loads(json_data)
        dataframes = {}
        for table_name, table_data in self.data.items():
            dataframes[table_name] = pd.DataFrame(table_data)

        for table_name, df in dataframes.items():
            df.to_sql(table_name, self.conn, index=False, if_exists="replace")

    async def __sendNewMessages__(self, new_message):
        if self.encryptKey != "":
            new_message = self.__encrypt__(new_message, self.encryptKey)

        await self.client.send_message(self.channel, new_message)

    async def connect(self):
        await self.client.start()

    async def initDatabase(self):
        self.channel_id = await self.client.get_entity(self.chanellInviteLink)
        self.channel = await self.client.get_entity(
            PeerChannel(int(self.channel_id.id))
        )
        file = open(self.databaseStructurePath, "r", encoding="utf-8")

        json_struct = file.read()

        messages = await self.__readRawDBJson__()

        if messages.startswith("#init") or messages == "":
            await self.__deleteAllMessages__()
            await self.__sendNewMessages__(json_struct)

        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    async def select(self, selectQuery):
        db_json = await self.__readRawDBJson__()
        self.__jsonToSqlite__(db_json)

        self.cursor.execute(selectQuery)
        rows = self.cursor.fetchall()

        return rows

    async def execute(self, query):

        if not hasattr(self, "data") or not self.data:
            db_json = await self.__readRawDBJson__()
            self.__jsonToSqlite__(db_json)

        self.cursor.execute(query)
        self.conn.commit()

        dataframes = {}
        for table_name in self.data.keys():
            dataframes[table_name] = pd.read_sql_query(
                f"SELECT * FROM {table_name}", self.conn
            )

        updated_data = {
            table_name: df.to_dict(orient="records")
            for table_name, df in dataframes.items()
        }

        # updated_json_data = json.dumps(updated_data, separators=(",", ":")  )
        updated_json_data = json.dumps(updated_data, indent=4)

        await self.__deleteAllMessages__()
        await self.__sendNewMessages__(updated_json_data)
