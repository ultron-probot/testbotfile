# =====================
# IMPORTS
# =====================
import os, asyncio, random, string
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
# BOT
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
    return "DEVIL" + ''.join(random.choices(string.digits, k=5))

def is_admin(uid):
    return uid in SUDO_USERS

# =====================
# START + REFERRAL
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

    await m.reply("🔒 Please complete verification")
  # =====================
# FORCE JOIN SYSTEM
# =====================

def force_buttons():
    btns = []
    row = []
    for ch in force.find():
        row.append(
            InlineKeyboardButton(
                ch["name"],
                url=ch["link"]
            )
        )
        if len(row) == 2:
            btns.append(row)
            row = []
    if row:
        btns.append(row)

    btns.append([InlineKeyboardButton("✅ VERIFY", callback_data="verify")])
    return InlineKeyboardMarkup(btns)

async def is_joined(client, uid):
    for ch in force.find():
        try:
            m = await client.get_chat_member(ch["chat_id"], uid)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


@bot.on_message(filters.command("addforcejoin") & filters.user(SUDO_USERS))
async def add_fj(c, m):
    try:
        _, name, link, chat_id = m.text.split()
        force.insert_one({
            "name": name,
            "link": link,
            "chat_id": int(chat_id)
        })
        await m.reply("✅ Force Join Added")
    except:
        await m.reply("/addforcejoin NAME LINK CHAT_ID")


@bot.on_message(filters.command("rmforcejoin") & filters.user(SUDO_USERS))
async def rm_fj(c, m):
    try:
        _, name = m.text.split()
        force.delete_one({"name": name})
        await m.reply("✅ Removed")
    except:
        await m.reply("/rmforcejoin NAME")


@bot.on_callback_query(filters.regex("verify"))
async def verify(c, q):
    if await is_joined(c, q.from_user.id):
        await q.message.edit("✅ Verified!\n\nUse menu now")
    else:
        await q.answer("❌ Join all channels first", show_alert=True)
# =====================
# FILE UPLOAD
# =====================

@bot.on_message(filters.command("upload") & filters.user(SUDO_USERS))
async def upload(c, m):
    if not m.reply_to_message:
        return await m.reply("Reply to a file")

    r = m.reply_to_message
    if not r.media:
        return await m.reply("Invalid file")

    code = gen_code()
    files.insert_one({
        "code": code,
        "file_id": r.media.file_id,
        "type": r.media.__class__.__name__
    })

    await m.reply(f"✅ File Stored\n\n🔑 Code: `{code}`")


@bot.on_message(filters.text & ~filters.command)
async def get_file(c, m):
    data = files.find_one({"code": m.text.strip()})
    if not data:
        return

    msg = await c.send_cached_media(
        m.chat.id,
        data["file_id"],
        caption="⚠️ Save this file\n⏱ Auto delete in 1 minute"
    )

    await asyncio.sleep(60)
    await msg.delete()
  # =====================
# ADD REWARD
# =====================
@bot.on_message(filters.command("addreward") & filters.user(SUDO_USERS))
async def add_reward(c, m):
    try:
        _, data = m.text.split(" ", 1)
        name, coins, deduct, limit, mode = [x.strip() for x in data.split("|")]

        rewards.insert_one({
            "name": name,
            "coins": int(coins),
            "deduct": deduct.lower() == "yes",
            "limit": int(limit),
            "mode": mode.lower()
        })

        await m.reply("✅ Reward Added")
    except:
        await m.reply(
            "/addreward Name | Coins | yes/no | Limit | on/off"
        )


@bot.on_message(filters.command("rmreward") & filters.user(SUDO_USERS))
async def rm_reward(c, m):
    try:
        _, name = m.text.split(" ", 1)
        rewards.delete_one({"name": name})
        await m.reply("✅ Reward Removed")
    except:
        await m.reply("/rmreward NAME")

  # =====================
# BROADCAST
# =====================

@bot.on_message(filters.command("broadcast") & filters.user(SUDO_USERS))
async def broadcast(c, m):
    mode = m.text.split()[1:] if len(m.text.split()) > 1 else []

    sent = 0
    for u in users.find():
        try:
            msg = await m.copy(u["user_id"])
            if "-pin" in mode:
                await msg.pin()
            sent += 1
        except:
            pass

    await m.reply(f"✅ Broadcast sent to {sent} users")
  # =====================
# STATS
# =====================
@bot.on_message(filters.command("stats") & filters.user(SUDO_USERS))
async def stats(c, m):
    await m.reply(
        f"""
📊 BOT STATS

👤 Users: {users.count_documents({})}
📁 Files: {files.count_documents({})}
🎁 Rewards: {rewards.count_documents({})}
🔒 Force Join: {force.count_documents({})}
"""
    )


# =====================
# SUDO
# =====================
@bot.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def add_sudo(c, m):
    uid = int(m.text.split()[1])
    SUDO_USERS.append(uid)
    await m.reply("✅ Sudo Added")


@bot.on_message(filters.command("rmsudo") & filters.user(OWNER_ID))
async def rm_sudo(c, m):
    uid = int(m.text.split()[1])
    SUDO_USERS.remove(uid)
    await m.reply("✅ Sudo Removed")
  # =====================
# MAIN MENU
# =====================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Free Rewards", callback_data="rewards")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")]
    ])


@bot.on_message(filters.command("menu"))
async def menu(c, m):
    if not await is_joined(c, m.from_user.id):
        return await m.reply(
            "🔒 Join required",
            reply_markup=force_buttons()
        )

    await m.reply(
        "🏠 Main Menu",
        reply_markup=main_menu()
    )


# =====================
# PROFILE
# =====================
@bot.on_callback_query(filters.regex("profile"))
async def profile(c, q):
    u = users.find_one({"user_id": q.from_user.id})
    await q.message.edit(
        f"""
👤 PROFILE

🆔 ID: `{q.from_user.id}`
💰 Coins: {u['coins']}
👥 Referrals: {u['referrals']}

🔗 Referral Link:
https://t.me/{(await c.get_me()).username}?start={q.from_user.id}
""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        )
  )

# =====================
# REWARDS MENU
# =====================

def rewards_menu():
    btns = []
    for r in rewards.find():
        btns.append(
            [InlineKeyboardButton(
                f"{r['name']} ({r['coins']}💰)",
                callback_data=f"claim_{r['name']}"
            )]
        )
    btns.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
    return InlineKeyboardMarkup(btns)


@bot.on_callback_query(filters.regex("rewards"))
async def rewards_cb(c, q):
    await q.message.edit(
        "🎁 Available Rewards",
        reply_markup=rewards_menu()
    )


@bot.on_callback_query(filters.regex("back"))
async def back_cb(c, q):
    await q.message.edit(
        "🏠 Main Menu",
        reply_markup=main_menu()
    )

# =====================
# CLAIM REWARD
# =====================

@bot.on_callback_query(filters.regex("^claim_"))
async def claim_reward(c, q):
    name = q.data.replace("claim_", "")
    r = rewards.find_one({"name": name})
    u = users.find_one({"user_id": q.from_user.id})

    claimed = u.get("claimed_rewards", {}).get(name, 0)

    if claimed >= r["limit"]:
        return await q.answer("❌ Claim limit reached", show_alert=True)

    if u["coins"] < r["coins"]:
        return await q.answer("❌ Insufficient coins", show_alert=True)

    # deduct coins
    if r["deduct"]:
        users.update_one(
            {"user_id": q.from_user.id},
            {"$inc": {"coins": -r["coins"]}}
        )

    # update claim
    users.update_one(
        {"user_id": q.from_user.id},
        {"$inc": {f"claimed_rewards.{name}": 1}}
    )

    if r["mode"] == "on":
        await q.message.edit(
            "📧 Send your email address to claim this reward"
        )
        users.update_one(
            {"user_id": q.from_user.id},
            {"$set": {"waiting_reward": name}}
        )
    else:
        await q.message.edit(
            f"✅ Reward Claimed\n\n{r.get('message','Thanks')}"
  )
# =====================
# EMAIL HANDLER
# =====================

@bot.on_message(filters.text & ~filters.command)
async def email_handler(c, m):
    u = users.find_one({"user_id": m.from_user.id})
    if not u or "waiting_reward" not in u:
        return

    reward_name = u["waiting_reward"]
    email = m.text

    await c.send_message(
        LOG_GROUP,
        f"""
🎁 REWARD CLAIMED

👤 User: @{m.from_user.username}
🆔 ID: {m.from_user.id}
🎁 Reward: {reward_name}
📧 Email: {email}
"""
    )

    users.update_one(
        {"user_id": m.from_user.id},
        {"$unset": {"waiting_reward": ""}}
    )

    await m.reply("✅ Reward request submitted successfully")
# =====================
# ANTI SPAM
# =====================
last_msg = {}

@bot.on_message(filters.private)
async def spam_control(c, m):
    uid = m.from_user.id
    now = datetime.utcnow().timestamp()

    if uid in last_msg and now - last_msg[uid] < 1:
        return await m.stop_propagation()

    last_msg[uid] = now
  @bot.on_message(filters.command("broadcast") & filters.user(SUDO_USERS))
async def bc(c, m):
    flags = m.text.split()
    pin = "-pin" in flags
    user_only = "-user" in flags

    sent = 0
    for u in users.find():
        try:
            msg = await m.copy(u["user_id"])
            if pin:
                await msg.pin()
            sent += 1
        except:
            pass

    await m.reply(f"✅ Broadcast sent: {sent}")
  print("🔥 FULL PREMIUM BOT RUNNING")
bot.run()


  
