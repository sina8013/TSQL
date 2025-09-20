import asyncio
import base64
import json
import random
import sqlite3
import time
from pathlib import Path

import pandas as pd
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2


class EncryptionHelper:
    """Handles AES encryption and decryption with password-based key derivation."""

    @staticmethod
    def _get_key(password: str, salt: bytes) -> bytes:
        return PBKDF2(password, salt, dkLen=32)

    @classmethod
    def encrypt(cls, plain_text: str, password: str) -> str:
        salt = get_random_bytes(16)
        key = cls._get_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM)
        cipher_text, tag = cipher.encrypt_and_digest(plain_text.encode("utf-8"))
        return base64.b64encode(salt + cipher.nonce + tag + cipher_text).decode("utf-8")

    @classmethod
    def decrypt(cls, encrypted_text: str, password: str) -> str:
        encrypted_data = base64.b64decode(encrypted_text)
        salt, nonce, tag, cipher_text = (
            encrypted_data[:16],
            encrypted_data[16:32],
            encrypted_data[32:48],
            encrypted_data[48:],
        )
        key = cls._get_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(cipher_text, tag).decode("utf-8")


class TSQL:
    """Telegram + SQLite bridge with optional AES encryption."""

    def __init__(self, api_id, api_hash, session_name, channel_link, db_schema_path, encrypt_key=""):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.channel_link = channel_link
        self.db_schema_path = Path(db_schema_path)
        self.encrypt_key = encrypt_key
        self.all_message_ids = []
        self.conn = None
        self.cursor = None
        self.data = {}

    async def connect(self):
        await self.client.start()
        print("[INFO] Connected to Telegram")

    async def _read_raw_db_json(self) -> str:
        """Fetches raw DB JSON from Telegram channel messages."""
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
        self.all_message_ids.clear()

        for message in history.messages:
            if message.message:
                self.all_message_ids.append(message.id)

                if message.message == "#init":
                    return "#init"

                db_raw += message.message

        if self.encrypt_key and db_raw:
            try:
                db_raw = EncryptionHelper.decrypt(db_raw, self.encrypt_key)
            except Exception as e:
                print(f"[ERROR] Failed to decrypt data: {e}")
                return ""

        return db_raw

    async def _delete_all_messages(self):
        """Deletes all messages in the channel (reset DB)."""
        await self._read_raw_db_json()
        if self.all_message_ids:
            await self.client.delete_messages(self.channel, self.all_message_ids)
            print(f"[INFO] Deleted {len(self.all_message_ids)} old messages")

    async def _send_new_message(self, content: str):
        """Sends new DB JSON to channel, encrypted if key provided."""
        if self.encrypt_key:
            content = EncryptionHelper.encrypt(content, self.encrypt_key)
        await self.client.send_message(self.channel, content)

    def _json_to_sqlite(self, json_data: str):
        """Loads JSON into in-memory SQLite database."""
        try:
            self.data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            self.data = {}
            return

        for table_name, records in self.data.items():
            df = pd.DataFrame(records)
            df.to_sql(table_name, self.conn, index=False, if_exists="replace")

    async def init_database(self):
        """Initialize Telegram channel DB with schema if empty."""
        self.channel_id = await self.client.get_entity(self.channel_link)
        self.channel = await self.client.get_entity(PeerChannel(int(self.channel_id.id)))

        schema = self.db_schema_path.read_text(encoding="utf-8")
        messages = await self._read_raw_db_json()

        if messages.startswith("#init") or not messages:
            await self._delete_all_messages()
            await self._send_new_message(schema)
            print("[INFO] Database initialized with schema")

        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    async def select(self, query: str):
        """Executes a SELECT query on the in-memory DB."""
        db_json = await self._read_raw_db_json()
        self._json_to_sqlite(db_json)

        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] Select query failed: {e}")
            return []

    async def execute(self, query: str):
        """Executes an INSERT/UPDATE/DELETE and pushes updates back to Telegram."""
        if not self.data:
            db_json = await self._read_raw_db_json()
            self._json_to_sqlite(db_json)

        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"[ERROR] Execute query failed: {e}")
            return

        # Reload all tables
        updated_data = {}
        for table_name in self.data.keys():
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            updated_data[table_name] = df.to_dict(orient="records")

        updated_json = json.dumps(updated_data, separators=(",", ":"))

        await self._delete_all_messages()
        await self._send_new_message(updated_json)
        print("[INFO] Database updated and synced with Telegram")
