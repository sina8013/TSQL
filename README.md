# 🚀 TSQL - Telegram SQLite Library

TSQL is a powerful Python library that synchronizes and manages SQLite databases through **Telegram channels**. With advanced encryption and real-time updates, TSQL makes database management and sharing simple and secure. 📦✨

---

## 🔑 Key Features

- **🔗 Telegram Integration**: Sync your SQLite database with Telegram channels seamlessly.
- **🔒 End-to-End Encryption**: Ensure data security using AES encryption.
- **⚡ Real-Time Updates**: Automatically manage database changes.
- **📊 Query Execution**: Execute custom SQL queries with ease.
- **📂 In-Memory SQLite**: Leverage fast and efficient in-memory SQLite databases.

---

## 🛠️ Installation

To install TSQL, use pip:

```bash
pip install tsql
```

---

## 📖 Usage

Here's how you can get started with TSQL:

```python
from tsql import TSQL
import asyncio

# Initialize the TSQL object
db = TSQL(
    api_id="12345",  # Your Telegram API ID
    api_hash="abcdef123456",  # Your Telegram API hash
    sessionName="my_session",  # Telegram session name
    chanellInviteLink="https://t.me/my_channel",  # Telegram channel invite link
    databaseStructurePath="db_structure.json",  # Path to your database structure file
    encryptKey="my_secret_key"  # (Optional) Encryption key for securing data
)

# Run asynchronously
async def main():
    await db.connect()  # Connect to Telegram
    await db.initDatabase()  # Initialize the database

    # Example: Execute a SELECT query
    result = await db.select("SELECT * FROM my_table;")
    print(result)

    # Example: Insert new data
    await db.execute("INSERT INTO my_table (id, name) VALUES (1, 'John Doe');")

# Run the async function
asyncio.run(main())
```

---

## 📂 Example Database Structure

TSQL uses JSON files to define your database structure. Here's an example:

```json
{
  "my_table": [
    { "id": 1, "name": "John Doe" },
    { "id": 2, "name": "Jane Doe" }
  ],
  "my_table_2": [
    { "id": 1, "name": "John Doe 2" },
    { "id": 2, "name": "Jane Doe 2" }
  ],
  "my_table_3": [
    { "id": 1, "name": "John Doe 3" },
    { "id": 2, "name": "Jane Doe 3" }
  ]
}
```

---

## 🧪 Testing

To run tests, ensure `pytest` is installed:

```bash
pip install pytest
pytest tests/
```

---

## 🌟 Why Use TSQL?

- 💡 **Innovative**: Use Telegram channels as a database synchronization medium.
- 🔐 **Secure**: Built-in AES encryption for data privacy.
- 🔄 **Dynamic**: Manage your database in real-time.
- 💻 **Developer-Friendly**: Easy-to-use interface for database operations.

---

## 👩‍💻 Contributing

We welcome contributions! Feel free to:

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push the branch: `git push origin feature-name`.
5. Open a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

Have questions or need support? Feel free to reach out:

- **Telegram**: [@YourTelegramHandle](https://t.me/sina8013)
- **Email**: sina8013@gmail.com

---

## 🚀 Get Started Today!

TSQL is the ultimate tool for managing and syncing your SQLite databases via Telegram. Install it now and simplify your database management process! 🎉
