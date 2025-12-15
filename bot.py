# =====================
# IMPORTS
# =====================
import os
import asyncio
import random
import string
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# =====================
# CONFIG
# =====================
API_ID = int(os.getenv("API_ID", "123"))
API_HASH = os.getenv("API_HASH", "API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID", "123456"))
LOG_GROUP = int(os.getenv("LOG_GROUP", "-100123"))

SUDO_USERS = [OWNER_ID]
MONGO_URL = os.getenv("MONGO_URL")

# =====================
# BOT INIT
# =====================
bot = Client("premiumbot", API_ID, API_HASH, bot_token=BOT_TOKEN)

mongo = MongoClient(MONGO_URL)
db = mongo["PremiumBot"]

users = db.users
files = db.files
force = db.force
rewards = db.rewards

# =====================
# UTILS
# =====================
def gen_code():
    return "DEVIL" + "".join(random.choices(string.digits, k=5))


async def is_joined(client, uid):
    for ch in force.find():
        try:
            m = await client.get_chat_member(ch["chat_id"], uid)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


def force_buttons():
    buttons = []
    row = []

    for ch in force.find():
        row.append(InlineKeyboardButton(ch["name"], url=ch["link"]))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("✅ VERIFY", callback_data="verify")])
    return InlineKeyboardMarkup(buttons)

# =====================
# START
# =====================
@bot.on_message(filters.command("start"))
async def start(client, m):
    uid = m.from_user.id
    args = m.text.split()

    if not users.find_one({"user_id": uid}):
        users.insert_one({
            "user_id": uid,
            "coins": 0,
            "referrals": 0,
            "claimed_rewards": {}
        })

        if len(args) > 1:
            ref = int(args[1])
            if ref != uid and users.find_one({"user_id": ref}):
                users.update_one(
                    {"user_id": ref},
                    {"$inc": {"coins": 10, "referrals": 1}}
                )

    await m.reply("🔒 Please complete verification", reply_markup=force_buttons())

# =====================
# FORCE JOIN
# =====================
@bot.on_callback_query(filters.regex("verify"))
async def verify(client, q):
    if await is_joined(client, q.from_user.id):
        await q.message.edit("✅ Verified!\n\nUse /menu")
    else:
        await q.answer("❌ Join all channels first", show_alert=True)

# =====================
# MENU
# =====================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Free Rewards", callback_data="rewards")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")]
    ])


@bot.on_message(filters.command("menu"))
async def menu(client, m):
    if not await is_joined(client, m.from_user.id):
        return await m.reply("🔒 Join required", reply_markup=force_buttons())

    await m.reply("🏠 Main Menu", reply_markup=main_menu())

# =====================
# PROFILE
# =====================
@bot.on_callback_query(filters.regex("profile"))
async def profile(client, q):
    u = users.find_one({"user_id": q.from_user.id})
    bot_user = await client.get_me()

    await q.message.edit(
        f"""
👤 PROFILE

🆔 ID: `{q.from_user.id}`
💰 Coins: {u['coins']}
👥 Referrals: {u['referrals']}

🔗 Referral Link:
https://t.me/{bot_user.username}?start={q.from_user.id}
""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        )
    )

# =====================
# BACK
# =====================
@bot.on_callback_query(filters.regex("back"))
async def back(client, q):
    await q.message.edit("🏠 Main Menu", reply_markup=main_menu())

# =====================
# FILE UPLOAD
# =====================
@bot.on_message(filters.command("upload") & filters.user(SUDO_USERS))
async def upload(client, m):
    if not m.reply_to_message or not m.reply_to_message.media:
        return await m.reply("Reply to a media file")

    code = gen_code()

    files.insert_one({
        "code": code,
        "file_id": m.reply_to_message.media.file_id
    })

    await m.reply(f"✅ File stored\n🔑 Code: `{code}`")


@bot.on_message(filters.text & ~filters.command)
async def get_file(client, m):
    data = files.find_one({"code": m.text.strip()})
    if not data:
        return

    msg = await client.send_cached_media(
        m.chat.id,
        data["file_id"],
        caption="⚠️ Save it\n⏱ Auto delete in 1 minute"
    )

    await asyncio.sleep(60)
    await msg.delete()

# =====================
# BROADCAST (SINGLE & CLEAN)
# =====================
@bot.on_message(filters.command("broadcast") & filters.user(SUDO_USERS))
async def broadcast(client, m):
    flags = m.text.split()
    pin = "-pin" in flags

    sent = 0
    for u in users.find():
        try:
            msg = await m.copy(u["user_id"])
            if pin:
                try:
                    await msg.pin()
                except:
                    pass
            sent += 1
        except:
            pass

    await m.reply(f"✅ Broadcast sent to {sent} users")

# =====================
# RUN
# =====================
print("🔥 FULL PREMIUM BOT RUNNING")
bot.run()
