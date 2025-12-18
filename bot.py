from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from pymongo import MongoClient
import datetime
import os

# ================= CONFIG ================= #

API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

MONGO_URL = os.getenv("MONGO_URL", "YOUR_MONGODB_ATLAS_URL")

# Multiple owner IDs (comma separated)
OWNER_IDS = list(map(int, os.getenv("OWNER_IDS", "123456789").split(",")))

LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1001234567890"))

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/yourgroup")
START_TELEGRAPH = os.getenv("START_TELEGRAPH", "https://telegra.ph/Welcome")

# ================= FORCE JOIN CONFIG ================= #

# 🔒 Force join verify (IDs only)
FORCE_CHANNELS = [
    -1003414102418,
    -1003414102418,
    -1003414102418
]

# 🔗 Force join buttons (links only)
FORCE_JOIN_LINKS = [
    "https://t.me/A2globalupdate",
    "https://t.me/A2globalupdate",
    "https://t.me/A2globalupdate"
]
BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBotUsername")

# ================= BOT ================= #

app = Client(
    "devilbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= DATABASE ================= #

mongo = MongoClient(MONGO_URL)
db = mongo["devilbot"]

users_col = db["users"]
premium_col = db["premium"]
codes_col = db["codes"]
history_col = db["history"]

# ================= HELPERS ================= #

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS

def get_time():
    return datetime.datetime.utcnow()

# ================= FORCE JOIN HELPERS ================= #

async def is_joined_all(client, user_id):
    for chat_id in FORCE_CHANNELS:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status == "left":
                return False
        except Exception as e:
            return False
    return True
    
def force_join_keyboard():
    join_buttons = []

    for link in FORCE_JOIN_LINKS:
        join_buttons.append(
            InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍", url=link)
        )

    return InlineKeyboardMarkup([
        join_buttons,  # 👈 3 join buttons ek line me
        [InlineKeyboardButton("✅ 🆅︎🅴︎🆁︎🅸︎🅵︎🆈︎", callback_data="verify_join")]
    ])
# ================= VERIFY FORCE JOIN ================= #

@app.on_callback_query(filters.regex("verify_join"))
async def verify_join(client, callback_query):
    user_id = callback_query.from_user.id

    if await is_joined_all(client, user_id):
    if await is_joined_all(client, user_id):
    try:
        await callback_query.message.edit_text(
            "✅ **𝐘𝐎𝐔𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋 😉!!**\n\n"
            "👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ɢɪᴠᴇᴀᴡᴀʏ ʙᴏᴛ!\n\n"
            "🎁 ᴇᴀʀɴ ᴘʀᴇᴍɪᴜᴍ ʙʏ ʀᴇғᴇʀʀɪɴɢ ᴜsᴇʀs\n"
            "🚀 sɪᴍᴘʟᴇ & ғᴀsᴛ ᴄʟᴀɪᴍɪɴɢ sʏsᴛᴇᴍ\n\n"
            "📢 **ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:**\n"
            "• sʜᴀʀᴇ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ\n"
            "• ᴄᴏᴍᴘʟᴇᴛᴇ ʀᴇǫᴜɪʀᴇᴅ ʀᴇғᴇʀʀᴀʟs ᴛᴏ ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ\n"
            "• ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴡᴀʀᴅ\n\n"
            "👇 **ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ:**",
            reply_markup=main_menu()
        )
    except:
        pass
    else:
        await callback_query.answer(
            "❌ Join all channels first!",
            show_alert=True
        )
        
# ================= START & MENU ================= #

def main_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ", callback_data="get_premium"),
                InlineKeyboardButton("😎 ᴘʀᴏғɪʟᴇ", callback_data="profile")
            ],
            [
                InlineKeyboardButton("🔗 ʀᴇғᴇʀ & ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ", callback_data="refer"),
                InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP)
            ],
            [
                InlineKeyboardButton("💌h ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=f"https://t.me/Ankitgupta2144")
            ]
        ]
    )

# ================= START (FINAL MERGED) ================= #

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    user_id = user.id
    username = user.username or "NoUsername"

    # 🔗 Referral parameter (FIRST)
    referrer_id = None
    if len(message.command) > 1:
        try:
            referrer_id = int(message.command[1])
        except:
            referrer_id = None

    user_data = users_col.find_one({"user_id": user_id})

    # 🆕 NEW USER INSERT + REFERRAL COUNT
    if not user_data:
        users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "referrals": 0,
            "referred_by": referrer_id,
            "claimed": 0,
            "premium_active_till": None,
            "join_date": get_time()
        })

        # ✅ REFERRAL COUNT (FIXED)
        if referrer_id and referrer_id != user_id:
            referrer = users_col.find_one({"user_id": referrer_id})
            if referrer:
                users_col.update_one(
                    {"user_id": referrer_id},
                    {"$inc": {"referrals": 1}}
                )

                try:
                    await client.send_message(
                        referrer_id,
                        "🎉 **ɴᴇᴡ ʀᴇғᴇʀʀᴀʟ ᴊᴏɪɴᴇᴅ!!**\nʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ ᴄᴏᴜɴᴛ ɪɴᴄʀᴇᴀsᴇᴅ ʙʏ 𝟷."
                    )
                except:
                    pass

    # 🔒 FORCE JOIN CHECK (AFTER REFERRAL)
    if not await is_joined_all(client, user_id):
        return await message.reply_text(
            "🔒 **ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ɢʀᴏᴜᴘs & ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ**",
            reply_markup=force_join_keyboard()
        )

    # 📢 LOG EVERY START
    await client.send_message(
        LOG_GROUP_ID,
        f"🚀 **𝐔𝐬𝐞𝐫 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐁𝐨𝐭**\n\n"
        f"👤 @{username}\n"
        f"🆔 `{user_id}`\n"
        f"👥 ʀᴇғᴇʀʀᴇᴅ ʙʏ: `{referrer_id}`\n"
        f"⏰ `{get_time()}`"
    )

    # 🎉 Welcome
    await message.reply_text(
        "👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ɢɪᴠᴇᴀᴡᴀʏ ʙᴏᴛ!\n\n"
            "🎁 ᴇᴀʀɴ ᴘʀᴇᴍɪᴜᴍ ʙʏ ʀᴇғᴇʀʀɪɴɢ ᴜsᴇʀs\n"
            "🚀 sɪᴍᴘʟᴇ & ғᴀsᴛ ᴄʟᴀɪᴍɪɴɢ sʏsᴛᴇᴍ\n\n"
            "📢 **ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:**\n"
            "• sʜᴀʀᴇ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ\n"
            "• ᴄᴏᴍᴘʟᴇᴛᴇ ʀᴇǫᴜɪʀᴇᴅ ʀᴇғᴇʀʀᴀʟs ᴛᴏ ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ\n"
            "• ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴡᴀʀᴅ\n\n"
        reply_markup=main_menu(),
        disable_web_page_preview=True
    )

# ================= BACK TO MENU ================= #

@app.on_callback_query(filters.regex("back_menu"))
async def back_menu(client, callback_query):
    try:
        await callback_query.message.edit_text(
            "👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ɢɪᴠᴇᴀᴡᴀʏ ʙᴏᴛ!\n\n"
            "🎁 ᴇᴀʀɴ ᴘʀᴇᴍɪᴜᴍ ʙʏ ʀᴇғᴇʀʀɪɴɢ ᴜsᴇʀs\n"
            "🚀 sɪᴍᴘʟᴇ & ғᴀsᴛ ᴄʟᴀɪᴍɪɴɢ sʏsᴛᴇᴍ\n\n"
            "📢 **ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:**\n"
            "• sʜᴀʀᴇ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ\n"
            "• ᴄᴏᴍᴘʟᴇᴛᴇ ʀᴇǫᴜɪʀᴇᴅ ʀᴇғᴇʀʀᴀʟs ᴛᴏ ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ\n"
            "• ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴡᴀʀᴅ\n\n"
            reply_markup=main_menu()
        )
    except:
        pass
# ================= REFERRAL Delt SYSTEM ================= #

# ================= REFER BUTTON ================= #

@app.on_callback_query(filters.regex("refer"))
async def refer_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"user_id": user_id})

    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    text = (
        "🔗 **ʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ**\n\n"
        f"`{link}`\n\n"
        "📢 sʜᴀʀᴇ ᴛʜɪs ʟɪɴᴋ ᴀɴᴅ ᴇᴀʀɴ ʀᴇғᴇʀʀᴀʟs.\n"
        "🎁 /ᴄᴏᴍᴘʟᴇᴛᴇ ʀᴇғᴇʀʀᴀʟs ᴛᴏ ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ!"
    )

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_menu")]]
        )
)
# ================= GET FREE PREMIUM ================= #

@app.on_callback_query(filters.regex("get_premium"))
async def get_premium(client, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"user_id": user_id})

    if not user:
        return await callback_query.answer("User not found!", show_alert=True)

    # Check active premium
    if user.get("premium_active_till"):
        if user["premium_active_till"] > get_time():
            return await callback_query.answer(
                "🤡ᴜʜʜ...ɴᴜғ..\n\n ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʙᴀʙʏ 🥵!!",
                show_alert=True
            )

    giveaway = premium_col.find_one({"active": True})
    if not giveaway:
        return await callback_query.answer(
            "❌ No active premium giveaway right now!",
            show_alert=True
        )

    required_refs = giveaway["required_refs"]

    if user["referrals"] < required_refs:
        return await callback_query.answer(
            f"ʏᴏᴜ ɴᴇᴇᴅ {required_refs} ʀᴇғᴇʀʀᴀʟs ᴛᴏ ᴄʟᴀɪᴍ ʏᴏᴜᴛᴜʙᴇ ᴘʀᴇᴍɪᴜᴍ ʙᴀʙʏ🥵🥵!",
            show_alert=True
        )

    await callback_query.message.edit_text(
        f"✅ **ʏᴏᴜ ᴀʀᴇ ᴇʟɪɢɪʙʟᴇ ᴛᴏ ᴄʟᴀɪᴍ ᴘʀᴇᴍɪᴜᴍ!**\n\n"
        f"🎁 ʀᴇᴡᴀʀᴅ: `{giveaway['reward']}`\n"
        f"📉 ʀᴇғᴇʀʀᴀʟs ᴛᴏ ᴅᴇᴅᴜᴄᴛ: `{required_refs}`\n\n"
        f"📧 **ɴᴏᴡ sᴇɴᴅ ʏᴏᴜʀ ᴇᴍᴀɪʟ ᴀᴅᴅʀᴇss ɪɴ ᴄʜᴀᴛ** ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ᴏɴ ʏᴏᴜʀ ᴍᴀɪʟ.\n\n ᴡᴀɪᴛ ғᴏʀ 𝟹 ʜʀs",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_menu")]]
        )
    )

    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"awaiting_email": True}}
    )


# ================= EMAIL COLLECT ================= #

@app.on_message(filters.text & ~filters.regex(r"^/"))
async def email_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"user_id": user_id})

    if not user or not user.get("awaiting_email"):
        return

    email = message.text.strip()
    giveaway = premium_col.find_one({"active": True})

    if not giveaway:
        return await message.reply_text("ɢɪᴠᴇᴀᴡᴀʏ ᴇxᴘɪʀᴇᴅ ᴏʀ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ʀɪɢʜᴛ ɴᴏᴡ.")

    active_till = get_time() + datetime.timedelta(
        days=giveaway["active_days"]
    )

    # Update user
    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "premium_active_till": active_till,
                "awaiting_email": False
            },
            "$inc": {
                "referrals": -giveaway["required_refs"],
                "claimed": 1
            }
        }
    )

    # Save history
    history_col.insert_one({
        "user_id": user_id,
        "email": email,
        "reward": giveaway["reward"],
        "time": get_time()
    })

    # Log group
    await client.send_message(
        LOG_GROUP_ID,
        f"🎉 **Pʀᴇᴍɪᴜᴍ Cʟᴀɪᴍᴇᴅ**\n\n"
        f"👤 ᴜsᴇʀ: @{message.from_user.username}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"📧 ᴇᴍᴀɪʟ: `{email}`\n"
        f"🎁 ʀᴇᴡᴀʀᴅ: `{giveaway['reward']}`\n"
        f"⏰ ᴛɪᴍᴇ: `{get_time()}`"
    )

    await message.reply_text(
        "🎉 **ᴘʀᴇᴍɪᴜᴍ ᴄʟᴀɪᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴏɴ ᴍᴀɪʟ!**\n\n"
        "📧 ʏᴏᴜʀ ᴇᴍᴀɪʟ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ғᴏʀ ᴀᴄᴛɪᴠᴀᴛɪᴏɴ.\n"
        "⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ʜᴏᴜʀs ғᴏʀ ʏᴏᴜʀ ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ ʙᴇᴇɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.",
        reply_markup=main_menu()
    )
# ================= PROFILE ================= #

@app.on_callback_query(filters.regex("profile"))
async def profile_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"user_id": user_id})

    if not user:
        return await callback_query.answer("ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!", show_alert=True)

    referrals = user.get("referrals", 0)
    claimed = user.get("claimed", 0)

    premium_till = user.get("premium_active_till")
    if premium_till and premium_till > get_time():
        status = "✅ ᴀᴄᴛɪᴠᴇ"
        till = premium_till.strftime("%d-%m-%Y %H:%M")
        can_claim = " Nᴏ (Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴇ)"
    else:
        status = "❌ ɴᴏᴛ ᴀᴄᴛɪᴠᴇ"
        till = "—"
        can_claim = "✅ ʏᴇs"

    text = (
        "👤 **ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ**\n\n"
        f"🆔 **ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
        f"👥 **ʀᴇғғᴇʀᴀʟs:** `{referrals}`\n"
        f"🎁 **ᴛᴏᴛᴀʟ ᴄʟᴀɪᴍs:** `{claimed}`\n\n"
        f"💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs:** {status}\n"
        f"⏳ **ᴀᴄᴛɪᴠᴇ ᴛɪʟʟ:** `{till}`\n\n"
        f"🛡 **ᴄᴀɴ ᴄʟᴀɪᴍ ɴᴇᴡ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴡᴀʀᴅ:** {can_claim}"
    )

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_menu")]]
        )
        )
# ================= TIME PARSER ================= #

def parse_time(text):
    total_seconds = 0
    num = ""

    for char in text:
        if char.isdigit():
            num += char
        else:
            if char == "h":
                total_seconds += int(num) * 3600
            elif char == "m":
                total_seconds += int(num) * 60
            elif char == "s":
                total_seconds += int(num)
            num = ""
    return total_seconds
# ================= ADD PREMIUM ================= #

@app.on_message(filters.command("addpremium"))
async def add_premium(client, message):
    if not is_owner(message.from_user.id):
        return

    try:
        _, amount, refs, active_time, per_user, months = message.text.split()
        amount = int(amount)
        refs = int(refs)
        per_user = int(per_user)
        months = int(months)

        seconds = parse_time(active_time)
        expire_at = get_time() + datetime.timedelta(seconds=seconds)

        premium_col.delete_many({})  # remove old giveaway

        premium_col.insert_one({
            "amount": amount,
            "required_refs": refs,
            "per_user": per_user,
            "active_till": expire_at,
            "active_days": months * 30,
            "reward": f"{months} Month Premium",
            "active": True,
            "created_at": get_time()
        })

        await message.reply_text(
            "✅ **Premium Giveaway Added Successfully!**\n\n"
            f"🎁 Reward: `{months} Month Premium`\n"
            f"👥 Required Referrals: `{refs}`\n"
            f"⏳ Active Till: `{expire_at}`\n"
            f"📦 Total Amount: `{amount}`"
        )

    except Exception as e:
        await message.reply_text(
            "❌ **ᴡʀᴏɴɢ ғᴏʀᴍᴀᴛ!**\n\n"
            "`/addpremium amount referrals time per_user months`\n"
            "Example:\n"
            "`/addpremium 50 5 24h 1 1`"
        )
# ================= REMOVE PREMIUM ================= #

@app.on_message(filters.command("rmpremium"))
async def remove_premium(client, message):
    if not is_owner(message.from_user.id):
        return

    premium_col.delete_many({})

    await message.reply_text("🗑 **Premium Giveaway Removed!**")
# ================= TIME PARSER (DAYS) ================= #

def parse_time_full(text):
    total_seconds = 0
    num = ""

    for char in text:
        if char.isdigit():
            num += char
        else:
            if char == "d":
                total_seconds += int(num) * 86400
            elif char == "h":
                total_seconds += int(num) * 3600
            elif char == "m":
                total_seconds += int(num) * 60
            elif char == "s":
                total_seconds += int(num)
            num = ""
    return total_seconds
import random
import string

# ================= GEN CODE ================= #

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@app.on_message(filters.command("gencode"))
async def gen_code(client, message):
    if not is_owner(message.from_user.id):
        return

    try:
        _, per_user, user_limit, active_time = message.text.split()
        per_user = int(per_user)
        user_limit = int(user_limit)

        seconds = parse_time_full(active_time)
        expire_at = get_time() + datetime.timedelta(seconds=seconds)

        code = generate_code()

        codes_col.insert_one({
            "code": code,
            "per_user": per_user,
            "user_limit": user_limit,
            "used_by": [],
            "expire_at": expire_at,
            "created_at": get_time()
        })

        await message.reply_text(
            "🎟 **Redeem Code Generated**\n\n"
            f"🔑 Code: `{code}`\n"
            f"👤 Per User: `{per_user}`\n"
            f"👥 User Limit: `{user_limit}`\n"
            f"⏳ Expire At: `{expire_at}`"
        )

    except:
        await message.reply_text(
            "❌ **ᴡʀᴏɴɢ ғᴏʀᴍᴀᴛ**\n\n"
            "`/gencode per_user user_limit time`\n"
            "Example:\n"
            "`/gencode 1 10 2d`"
                )
# ================= REMOVE CODE ================= #

@app.on_message(filters.command("rmcode"))
async def remove_code(client, message):
    if not is_owner(message.from_user.id):
        return

    try:
        _, code = message.text.split()
        result = codes_col.delete_one({"code": code})

        if result.deleted_count:
            await message.reply_text("🗑 **Code removed successfully!**")
        else:
            await message.reply_text("😔 ᴄᴏᴅᴇ ɴᴏᴛ ғᴏᴜɴᴅ!")

    except:
        await message.reply_text("❌ Use: `/rmcode CODE`")
# ================= REDEEM CODE (USER) ================= #

@app.on_message(filters.text & ~filters.regex(r"^/"))
async def redeem_code_handler(client, message):
    user_id = message.from_user.id
    text = message.text.strip().upper()

    code_data = codes_col.find_one({"code": text})
    if not code_data:
        return

    # Expiry check
    if code_data["expire_at"] < get_time():
        return await message.reply_text("🤐 ᴛʜɪs ᴄᴏᴅᴇ ʜᴀs ᴇxᴘɪʀᴇᴅ!")

    # User limit check
    if len(code_data["used_by"]) >= code_data["user_limit"]:
        return await message.reply_text("😬😮‍💨 ɴᴏ ʙᴀʙʏ ᴜʀ ʟᴀᴛᴇ ᴄᴏᴅᴇ ᴜsᴀɢᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ!!")

    # Per user check
    if code_data["used_by"].count(user_id) >= code_data["per_user"]:
        return await message.reply_text("❌ You already used this code!")

    # Active premium check
    user = users_col.find_one({"user_id": user_id})
    if user.get("premium_active_till") and user["premium_active_till"] > get_time():
        return await message.reply_text("❌ You already have active premium!")

    # Activate premium (default 30 days)
    active_till = get_time() + datetime.timedelta(days=30)

    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"premium_active_till": active_till}}
    )

    codes_col.update_one(
        {"code": text},
        {"$push": {"used_by": user_id}}
    )

    await client.send_message(
        LOG_GROUP_ID,
        f"🎟 **Redeem Code Used**\n\n"
        f"👤 User: @{message.from_user.username}\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔑 Code: `{text}`\n"
        f"⏰ Time: `{get_time()}`"
    )

    await message.reply_text(
        "✅ **ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ᴠɪᴀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇe!**\n"
        f"⏳ ᴀᴄᴛɪᴠᴇ ᴛɪʟʟ: `{active_till}`",
        reply_markup=main_menu()
        )

# ================= REDEEM COMMAND ================= #

@app.on_message(filters.command("redeem"))
async def redeem_command(client, message):
    user_id = message.from_user.id

    if len(message.command) != 2:
        return await message.reply_text(
            "❌ **ᴡʀᴏɴɢ ғᴏʀᴍᴀᴛ**\n\nUse:\n`/redeem CODE`"
        )

    code = message.command[1].upper()
    code_data = codes_col.find_one({"code": code})

    if not code_data:
        return await message.reply_text("❌ Invalid redeem code!")

    # Expiry check
    if code_data["expire_at"] < get_time():
        return await message.reply_text("🤐 ᴛʜɪs ᴄᴏᴅᴇ ʜᴀs ᴇxᴘɪʀᴇᴅ!")

    # User limit check
    if len(code_data["used_by"]) >= code_data["user_limit"]:
        return await message.reply_text("❌ Code usage limit reached!")

    # Per user check
    if user_id in code_data["used_by"]:
        return await message.reply_text("❌ You already used this code!")

    user = users_col.find_one({"user_id": user_id})

    # ❌ ACTIVE PREMIUM CHECK REMOVED (AS YOU REQUESTED)

    # Activate premium (30 days default)
    active_till = get_time() + datetime.timedelta(days=30)

    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "premium_active_till": active_till,
                "awaiting_email": True
            }
        }
    )

    codes_col.update_one(
        {"code": code},
        {"$push": {"used_by": user_id}}
    )

    await client.send_message(
        LOG_GROUP_ID,
        f"🎟 **Redeem Used**\n\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 `{user_id}`\n"
        f"🔑 `{code}`\n"
        f"⏰ `{get_time()}`"
    )

    await message.reply_text(
        "🎉 **ʏᴏᴜ ʜᴀᴠᴇ ᴄʟᴀɪᴍᴇᴅ ʏᴏᴜᴛᴜʙᴇ ᴘʀᴇᴍɪᴜᴍ!**\n\n"
        "📧 **ɴᴏᴡ sᴇɴᴅ ʏᴏᴜʀ ᴇᴍᴀɪʟ ᴀᴅᴅʀᴇss ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴏɴ ᴍᴀɪʟ.**"
    )
#================= BROADCAST ================= #

@app.on_message(filters.command("broadcast"))
async def broadcast_handler(client, message):
    if not is_owner(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("❌ Use: `/broadcast your message`")

    text = message.text.split(None, 1)[1]
    sent = 0
    failed = 0

    for user in users_col.find():
        try:
            await client.send_message(
                user["user_id"],
                text
            )
            sent += 1
        except:
            failed += 1

    await message.reply_text(
        f"📢 **Broadcast Completed**\n\n"
        f"✅ Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`"
    )


# ================= BROADCAST PIN ================= #

@app.on_message(filters.command("broadcastpin"))
async def broadcast_pin_handler(client, message):
    if not is_owner(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("❌ Use: `/broadcastpin your message`")

    text = message.text.split(None, 1)[1]
    sent = 0
    failed = 0

    for user in users_col.find():
        try:
            msg = await client.send_message(
                user["user_id"],
                text
            )
            await msg.pin(disable_notification=True)
            sent += 1
        except:
            failed += 1

    await message.reply_text(
        f"📌 **Broadcast Pin Completed**\n\n"
        f"✅ Sent & Pinned: `{sent}`\n"
        f"❌ Failed: `{failed}`"
    )
# ================= STATS ================= #

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    if not is_owner(message.from_user.id):
        return

    now = get_time()
    today = now - datetime.timedelta(days=1)
    week = now - datetime.timedelta(days=7)
    month = now - datetime.timedelta(days=30)

    total_users = users_col.count_documents({})
    today_claims = history_col.count_documents({"time": {"$gte": today}})
    week_claims = history_col.count_documents({"time": {"$gte": week}})
    month_claims = history_col.count_documents({"time": {"$gte": month}})

    text = (
        "📊 **Bot Statistics**\n\n"
        f"👥 Total Users: `{total_users}`\n\n"
        f"🎁 Claims Today: `{today_claims}`\n"
        f"🎁 Claims This Week: `{week_claims}`\n"
        f"🎁 Claims This Month: `{month_claims}`"
    )

    await message.reply_text(text)
# ================= USERS LIST ================= #

@app.on_message(filters.command("users"))
async def users_handler(client, message):
    if not is_owner(message.from_user.id):
        return

    text = "👥 **Users List**\n\n"
    count = 0

    for user in users_col.find():
        count += 1
        premium = user.get("premium_active_till")
        status = "Active" if premium and premium > get_time() else "No"

        text += (
            f"{count}. @{user.get('username','NoUsername')} | "
            f"ID: `{user['user_id']}` | "
            f"Refs: `{user.get('referrals',0)}` | "
            f"Claims: `{user.get('claimed',0)}` | "
            f"Premium: `{status}`\n"
        )

        if count % 20 == 0:
            await message.reply_text(text)
            text = ""

    if text:
        await message.reply_text(text)
# ================= HISTORY ================= #

@app.on_message(filters.command("history"))
async def history_handler(client, message):
    if not is_owner(message.from_user.id):
        return

    now = get_time() - datetime.timedelta(days=30)
    total_claims = history_col.count_documents({"time": {"$gte": now}})

    # Top referrer
    top = users_col.find().sort("referrals", -1).limit(1)
    top_user = next(top, None)

    text = (
        "📜 **Monthly History**\n\n"
        f"🎁 Total Claims (30 days): `{total_claims}`\n\n"
    )

    if top_user:
        text += (
            "🏆 **Top Referrer**\n"
            f"👤 @{top_user.get('username','NoUsername')}\n"
            f"👥 Referrals: `{top_user.get('referrals',0)}`"
        )

    await message.reply_text(text)
# ================= HELP ================= #

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    if not is_owner(message.from_user.id):
        return

    text = (
        "🆘 **Admin Commands Help**\n\n"
        "/addpremium <amount> <refs> <time> <per_user> <months>\n"
        "/rmpremium\n\n"
        "/gencode <per_user> <user_limit> <time>\n"
        "/rmcode <CODE>\n\n"
        "/broadcast <message>\n"
        "/broadcastpin <message>\n\n"
        "/stats\n"
        "/users\n"
        "/history\n"
    )

    await message.reply_text(text)
# ================= START BOT ================= #

print("🔥 DEVIL BOT STARTED SUCCESSFULLY 🔥 ENJOY IT BABY 🥵🔥")

app.run()
