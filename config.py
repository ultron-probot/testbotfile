import os

API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "API_HASH_HERE")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKEN_HERE")

OWNER_ID = int(os.environ.get("OWNER_ID", 6135117014))
LOG_GROUP = int(os.environ.get("LOG_GROUP", -1003415074133))

START_IMAGE = os.environ.get(
    "START_IMAGE",
    "https://files.catbox.moe/8a3dum.jpg"
)

JOIN1 = os.environ.get("JOIN1", "https://t.me/A2globalupdate")
JOIN2 = os.environ.get("JOIN2", "https://t.me/A2globalupdate")
JOIN3 = os.environ.get("JOIN3", "https://t.me/A2globalupdate")
