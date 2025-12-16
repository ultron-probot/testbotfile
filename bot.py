from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import json, os

from config import *

DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "users": {},
            "settings": {
                "reward_need": 5,
                "reward_deduct": 5,
                "claim_limit": 1
            },
            "sudo": []
        }
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load_db()

def get_user(uid):
    uid = str(uid)
    if uid not in db["users"]:
        db["users"][uid] = {
            "ref": 0,
            "bonus": 0,
            "claimed": 0,
            "banned": False,
            "waiting_email": False
        }
    return db["users"][uid]

def is_admin(uid):
    return uid == OWNER_ID or uid in db["sudo"]

app = Client(
    "rewardbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def check_force_join(uid):
    for ch in [JOIN1, JOIN2, JOIN3]:
        if ch:
            try:
                await app.get_chat_member(ch.split("/")[-1], uid)
            except UserNotParticipant:
                return False
    return True

def force_buttons():
    btn = []
    if JOIN1:
        btn.append([InlineKeyboardButton("Join 1", url=JOIN1)])
    if JOIN2:
        btn.append([InlineKeyboardButton("Join 2", url=JOIN2)])
    if JOIN3:
        btn.append([InlineKeyboardButton("Join 3", url=JOIN3)])
    btn.append([InlineKeyboardButton("✅ Verify", callback_data="verify")])
    return InlineKeyboardMarkup(btn)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Free Reward", callback_data="reward")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("📣 Refer & Get Premium", callback_data="refer")],
        [InlineKeyboardButton("👨‍💻 Developer", callback_data="dev")]
    ])

@app.on_message(filters.command("start"))
async def start(_, m):
    uid = m.from_user.id
    args = m.text.split()
    user = get_user(uid)

    if user["banned"]:
        return await m.reply("❌ You are banned.")

    if len(args) == 2:
        ref = args[1]
        if ref != str(uid) and ref in db["users"]:
            db["users"][ref]["ref"] += 1
            db["users"][ref]["bonus"] += 1
            save_db()

    await app.send_message(
        LOG_GROUP,
        f"🚀 Bot Started\nID: {uid}\nUsername: @{m.from_user.username}"
    )

    await m.reply_photo(
        START_IMAGE,
        caption="🎁 Welcome\n\nJoin all channels then verify",
        reply_markup=force_buttons()
    )

@app.on_callback_query(filters.regex("verify"))
async def verify(_, cb):
    if not await check_force_join(cb.from_user.id):
        return await cb.answer("❌ Join all channels", show_alert=True)

    await cb.message.edit_caption(
        "✅ Verified Successfully",
        reply_markup=main_menu()
    )

@app.on_callback_query(filters.regex("profile"))
async def profile(_, cb):
    u = get_user(cb.from_user.id)
    bot = await app.get_me()
    txt = (
        f"👤 Profile\n\n"
        f"ID: {cb.from_user.id}\n"
        f"Referrals: {u['ref']}\n"
        f"Bonus: {u['bonus']}\n"
        f"Claimed: {u['claimed']}\n\n"
        f"🔗 Referral Link:\n"
        f"https://t.me/{bot.username}?start={cb.from_user.id}"
    )
    await cb.message.edit_caption(
        txt,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅ Back", callback_data="verify")]]
        )
    )

@app.on_callback_query(filters.regex("refer"))
async def refer(_, cb):
    bot = await app.get_me()
    await cb.message.edit_caption(
        f"📣 Share link & earn\n\nhttps://t.me/{bot.username}?start={cb.from_user.id}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅ Back", callback_data="verify")]]
        )
    )

@app.on_callback_query(filters.regex("dev"))
async def dev(_, cb):
    await cb.message.edit_caption(
        f"👨‍💻 Developer ID:\n`{OWNER_ID}`",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅ Back", callback_data="verify")]]
        )
    )

@app.on_callback_query(filters.regex("reward"))
async def reward(_, cb):
    u = get_user(cb.from_user.id)
    s = db["settings"]

    if u["claimed"] >= s["claim_limit"]:
        return await cb.answer("❌ Claim limit reached", show_alert=True)

    if u["bonus"] < s["reward_need"]:
        return await cb.answer("❌ Not enough referrals", show_alert=True)

    u["bonus"] -= s["reward_deduct"]
    u["claimed"] += 1
    u["waiting_email"] = True
    save_db()

    await app.send_message(
        LOG_GROUP,
        f"🎁 Reward Claimed\nID: {cb.from_user.id}\nUsername: @{cb.from_user.username}"
    )

    await cb.message.edit_caption(
        "📧 Send your Email ID\n(YouTube Premium – 1 Month)",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅ Back", callback_data="verify")]]
        )
    )
@app.on_message(filters.text & ~filters.command([]))
async def email_handler(_, m):
    u = get_user(m.from_user.id)
    if u["waiting_email"]:
        u["waiting_email"] = False
        save_db()
        await app.send_message(
            LOG_GROUP,
            f"📩 Premium Email\nID: {m.from_user.id}\nEmail: {m.text}"
        )
        await m.reply("✅ Email received. Activation soon.")

# ---------- ADMIN COMMANDS ----------

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(_, m):
    pin = "-pin" in m.text
    text = m.text.replace("/broadcast", "").replace("-pin", "").strip()
    for uid in db["users"]:
        try:
            msg = await app.send_message(int(uid), text)
            if pin:
                await msg.pin()
        except:
            pass
    await m.reply("✅ Broadcast done")

@app.on_message(filters.command("addreward") & filters.user(OWNER_ID))
async def addreward(_, m):
    _, need, limit, deduct = m.text.split()
    db["settings"]["reward_need"] = int(need)
    db["settings"]["claim_limit"] = int(limit)
    db["settings"]["reward_deduct"] = int(deduct)
    save_db()
    await m.reply("✅ Reward updated")

@app.on_message(filters.command("addsudouser") & filters.user(OWNER_ID))
async def addsudo(_, m):
    uid = int(m.text.split()[1])
    if uid not in db["sudo"]:
        db["sudo"].append(uid)
        save_db()
    await m.reply("✅ Sudo added")

@app.on_message(filters.command("rmsudouser") & filters.user(OWNER_ID))
async def rmsudo(_, m):
    uid = int(m.text.split()[1])
    if uid in db["sudo"]:
        db["sudo"].remove(uid)
        save_db()
    await m.reply("✅ Sudo removed")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(_, m):
    await m.reply(
        f"📊 Stats\n\nUsers: {len(db['users'])}\nSudo: {len(db['sudo'])}"
    )

@app.on_message(filters.command("userlist") & filters.user(OWNER_ID))
async def userlist(_, m):
    txt = ""
    for uid, u in db["users"].items():
        txt += f"{uid} | Ref:{u['ref']} | Bonus:{u['bonus']} | Claimed:{u['claimed']}\n"
    await m.reply(txt or "No users")

@app.on_message(filters.command("banuser") & filters.user(OWNER_ID))
async def ban(_, m):
    uid = m.text.split()[1]
    get_user(uid)["banned"] = True
    save_db()
    await m.reply("✅ User banned")

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban(_, m):
    uid = m.text.split()[1]
    get_user(uid)["banned"] = False
    save_db()
    await m.reply("✅ User unbanned")

print("Bot Started Successfully")
app.run()
