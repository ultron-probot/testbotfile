import os

API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "API_HASH_HERE")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKEN_HERE")

OWNER_ID = int(os.environ.get("OWNER_ID", 123456789))
LOG_GROUP = int(os.environ.get("LOG_GROUP", -100123456789))

START_IMAGE = os.environ.get(
    "START_IMAGE",
    "https://telegra.ph/file/example.jpg"
)

JOIN1 = os.environ.get("JOIN1", "")
JOIN2 = os.environ.get("JOIN2", "")
JOIN3 = os.environ.get("JOIN3", "")
