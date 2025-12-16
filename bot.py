from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient
import os, random, string, time, asyncio

from config import *

# ---------------- MONGO SETUP ----------------
mongo = MongoClient(MONGO_URI)
mdb = mongo["reward_bot"]

users_col = mdb["users"]
settings_col = mdb["settings"]
sudo_col = mdb["sudo"]
files_col = mdb["files"]

if not settings_col.find_one({"_id": "config"}):
    settings_col.insert_one({
        "_id": "config",
        "reward_need": 5,
        "reward_deduct": 5,
        "claim_limit": 1
    })

# ---------------- HELPERS ----------------
def is_admin(uid):
    return uid == OWNER_ID or sudo_col.find_one({"_id": uid})

def get_user(uid):
    u = users_col.find_one({"_id": uid})
    if not u:
        u = {
            "_id": uid,
            "ref": 0,
            "bonus": 0,
            "claimed": 0,
            "banned": False,
            "waiting_email": False
        }
        users_col.insert_one(u)
    return u

def gen_code():
    return "DEVIL" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ---------------- BOT ----------------
app = Client(
    "rewardbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- FORCE JOIN ----------------
async def check_force_join(uid):
    for ch in [JOIN1, JOIN2, JOIN3]:
        if not ch:
            continue
        try:
            member = await app.get_chat_member(ch.split("/")[-1], uid)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def force_buttons():
    btn = []
    if JOIN1: btn.append([InlineKeyboardButton("Join 1", url=JOIN1)])
    if JOIN2: btn.append([InlineKeyboardButton("Join 2", url=JOIN2)])
    if JOIN3: btn.append([InlineKeyboardButton("Join 3", url=JOIN3)])
    btn.append([InlineKeyboardButton("✅ Verify", callback_data="verify")])
    return InlineKeyboardMarkup(btn)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Free Reward", callback_data="reward")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("📣 Refer & Get Premium", callback_data="refer")],
        [InlineKeyboardButton("👨‍💻 Developer", callback_data="dev")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, m):
    uid = m.from_user.id
    args = m.command

    u = get_user(uid)
    if u["banned"]:
        return await m.reply("❌ You are banned.")

    if len(args) == 2:
        ref = int(args[1])
        if ref != uid and users_col.find_one({"_id": ref}):
            users_col.update_one({"_id": ref}, {"$inc": {"ref": 1, "bonus": 1}})

    await app.send_message(
        LOG_GROUP,
        f"🚀 Bot Started\nID: {uid}\nUsername: @{m.from_user.username}"
    )

    await m.reply_photo(
        START_IMAGE,
        caption="🎁 Welcome\n\nJoin all channels then verify",
        reply_markup=force_buttons()
    )

# ---------------- VERIFY ----------------
@app.on_callback_query(filters.regex("verify"))
async def verify(_, cb):
    if not await check_force_join(cb.from_user.id):
        return await cb.answer("❌ Join all channels first", show_alert=True)

    await cb.message.edit_caption(
        "✅ Verified Successfully",
        reply_markup=main_menu()
    )

# ---------------- MENU ----------------
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
        f"https://t.me/{bot.username}?start={cb.from_user.id}"
    )
    await cb.message.edit_caption(txt, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅ Back", callback_data="verify")]]
    ))

@app.on_callback_query(filters.regex("refer"))
async def refer(_, cb):
    bot = await app.get_me()
    await cb.message.edit_caption(
        f"📣 Share this link:\nhttps://t.me/{bot.username}?start={cb.from_user.id}",
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

# ---------------- REWARD ----------------
@app.on_callback_query(filters.regex("reward"))
async def reward(_, cb):
    s = settings_col.find_one({"_id": "config"})
    u = get_user(cb.from_user.id)

    if u["claimed"] >= s["claim_limit"]:
        return await cb.answer("❌ Claim limit reached", show_alert=True)

    if u["bonus"] < s["reward_need"]:
        return await cb.answer("❌ Not enough referrals", show_alert=True)

    users_col.update_one(
        {"_id": cb.from_user.id},
        {"$inc": {"bonus": -s["reward_deduct"], "claimed": 1},
         "$set": {"waiting_email": True}}
    )

    await app.send_message(
        LOG_GROUP,
        f"🎁 Reward Claimed\nID: {cb.from_user.id}"
    )

    await cb.message.edit_caption(
        "📧 Send your Email ID\n(YouTube Premium – 1 Month)",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅ Back", callback_data="verify")]]
        )
    )

@app.on_message(filters.text & ~filters.command([]))
async def text_handler(_, m):
    u = get_user(m.from_user.id)

    # Email handler
    if u["waiting_email"]:
        users_col.update_one(
            {"_id": m.from_user.id},
            {"$set": {"waiting_email": False}}
        )
        await app.send_message(
            LOG_GROUP,
            f"📩 Premium Email\nID: {m.from_user.id}\nEmail: {m.text}"
        )
        return await m.reply("✅ Email received. Activation soon.")

    # File fetch
    code = m.text.strip().upper()
    f = files_col.find_one({"_id": code})
    if not f:
        return

    sent = await app.send_cached_media(
        m.chat.id,
        f["file_id"],
        caption="⚠️ Copyright Protected\n\nSave it now.\nAuto delete in 60 seconds."
    )

    await asyncio.sleep(60)
    try:
        await sent.delete()
    except:
        pass

# ---------------- FILE UPLOAD ----------------
@app.on_message(filters.command("uploadfile"))
async def upload(_, m):
    if not is_admin(m.from_user.id):
        return
    await m.reply("📤 Send the file")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def receive_file(_, m):
    if not is_admin(m.from_user.id):
        return

    code = gen_code()
    file_id = (
        m.document.file_id if m.document else
        m.video.file_id if m.video else
        m.audio.file_id if m.audio else
        m.photo.file_id
    )

    files_col.insert_one({
        "_id": code,
        "file_id": file_id,
        "by": m.from_user.id,
        "time": int(time.time())
    })

    await app.send_message(LOG_GROUP, f"📁 File Stored\nCode: `{code}`")
    await m.reply(f"✅ File Uploaded\n\n🔑 Code: `{code}`")

@app.on_message(filters.command("delupload"))
async def delupload(_, m):
    if not is_admin(m.from_user.id):
        return
    if len(m.command) != 2:
        return await m.reply("Usage: /delupload CODE")

    code = m.command[1].upper()
    if not files_col.find_one({"_id": code}):
        return await m.reply("❌ Code not found")

    files_col.delete_one({"_id": code})
    await m.reply("✅ File deleted")

# ---------------- ADMIN COMMANDS ----------------
@app.on_message(filters.command("help"))
async def help_cmd(_, m):
    if not is_admin(m.from_user.id):
        return
    await m.reply(
        "🛠 ADMIN COMMANDS\n\n"
        "/broadcast <msg>\n"
        "/broadcast -pin <msg>\n"
        "/addreward <need> <limit> <deduct>\n"
        "/addsudouser <id>\n"
        "/rmsudouser <id>\n"
        "/stats\n"
        "/userlist\n"
        "/banuser <id>\n"
        "/unban <id>\n"
        "/uploadfile\n"
        "/delupload <code>\n"
    )

@app.on_message(filters.command("broadcast"))
async def broadcast(_, m):
    if not is_admin(m.from_user.id):
        return
    pin = "-pin" in m.text
    text = m.text.replace("/broadcast", "").replace("-pin", "").strip()

    for u in users_col.find():
        try:
            msg = await app.send_message(u["_id"], text)
            if pin:
                await msg.pin()
        except:
            pass
    await m.reply("✅ Broadcast done")

@app.on_message(filters.command("addreward") & filters.user(OWNER_ID))
async def addreward(_, m):
    _, need, limit, deduct = m.command
    settings_col.update_one(
        {"_id": "config"},
        {"$set": {
            "reward_need": int(need),
            "claim_limit": int(limit),
            "reward_deduct": int(deduct)
        }}
    )
    await m.reply("✅ Reward updated")

@app.on_message(filters.command("addsudouser") & filters.user(OWNER_ID))
async def addsudo(_, m):
    uid = int(m.command[1])
    sudo_col.update_one({"_id": uid}, {"$set": {"_id": uid}}, upsert=True)
    await m.reply("✅ Sudo added")

@app.on_message(filters.command("rmsudouser") & filters.user(OWNER_ID))
async def rmsudo(_, m):
    sudo_col.delete_one({"_id": int(m.command[1])})
    await m.reply("✅ Sudo removed")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(_, m):
    await m.reply(
        f"📊 Stats\nUsers: {users_col.count_documents({})}\nFiles: {files_col.count_documents({})}"
    )

@app.on_message(filters.command("userlist") & filters.user(OWNER_ID))
async def userlist(_, m):
    txt = ""
    for u in users_col.find():
        txt += f"{u['_id']} | Ref:{u['ref']} | Bonus:{u['bonus']} | Claimed:{u['claimed']}\n"
    await m.reply(txt or "No users")

@app.on_message(filters.command("banuser") & filters.user(OWNER_ID))
async def ban(_, m):
    users_col.update_one({"_id": int(m.command[1])}, {"$set": {"banned": True}})
    await m.reply("✅ User banned")

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban(_, m):
    users_col.update_one({"_id": int(m.command[1])}, {"$set": {"banned": False}})
    await m.reply("✅ User unbanned")

print("🔥 Bot Started Successfully")
app.run()
