import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pymongo import MongoClient

# ==== CONFIG ====
BOT_TOKEN = "8370711516:AAEtXRjArAKwTlcZfx4dzd5E_aiIvcs4yvU"
MONGO_URI = "mongodb+srv://afzal99550:afzal99550@cluster0.aqmbh9q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
OWNER_IDS = [7270006608]  # <-- Apna Telegram ID yaha daalna hai

# ==== MongoDB Setup ====
mongo = MongoClient(MONGO_URI)
db = mongo["botdb"]
users_col = db["users"]
blocked_col = db["blocked_users"]

# ==== Image URLs ====
START_IMAGE = "https://i.ibb.co/Mk5jTp1s/x.jpg"
PREMIUM_IMAGE = "https://i.ibb.co/WSzsgXQ/x.jpg"

# ==== Messages ====
START_MESSAGE = (
    "𝗗𝗶𝗿𝗲𝗰𝘁 𝗣#𝗿𝗻 𝗩𝗶𝗱𝗲𝗼 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 🌸\n\n"
    "𝗗#𝘀𝗶 𝗠𝗮𝗮𝗹 𝗞𝗲 𝗗𝗲𝗲𝘄𝗮𝗻𝗼 𝗞𝗲 𝗟𝗶𝘆𝗲 😋\n\n"
    "𝗡𝗼 𝗦𝗻#𝗽𝘀 𝗣𝘂𝗿𝗲 𝗗#𝘀𝗶 𝗠𝗮𝗮𝗹 😙\n\n"
    "𝟱𝟭𝟬𝟬𝟬+ 𝗿𝗮𝗿𝗲 𝗗#𝘀𝗶 𝗹𝗲#𝗸𝘀 𝗲𝘃𝗲𝗿.... 🎀\n\n"
    "𝗣𝗿𝗶𝗰𝗲 :- ₹99/-"
)

PREMIUM_MESSAGE = (
    "💎 Premium Access Details\n\n"
    "Pay just ₹99/- and get lifetime access!\n\n"
    "Send your payment screenshot to @mmsbhai069 ✅"
)

# ==== Save Users in Mongo ====
async def save_user(update: Update):
    chat = update.effective_chat
    user_id = chat.id
    chat_type = chat.type
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {
                "chat_type": chat_type,
                "username": update.effective_user.username if update.effective_user else None,
            }
        },
        upsert=True
    )

# ==== Block / Unblock System ====
async def is_blocked(user_id: int):
    return blocked_col.find_one({"_id": user_id}) is not None

async def check_block(update: Update):
    user = update.effective_user
    if user and await is_blocked(user.id):
        try:
            await update.message.reply_text("🚫 You can't access this bot.")
        except Exception:
            pass
        return True
    return False

async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("⛔ You are not allowed to use this command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /block <user_id>")
        return
    try:
        target_id = int(context.args[0])
        blocked_col.update_one({"_id": target_id}, {"$set": {"blocked": True}}, upsert=True)
        await update.message.reply_text(f"🚫 User {target_id} has been blocked.")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid user ID format.")

async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("⛔ You are not allowed to use this command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unblock <user_id>")
        return
    try:
        target_id = int(context.args[0])
        blocked_col.delete_one({"_id": target_id})
        await update.message.reply_text(f"✅ User {target_id} has been unblocked.")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid user ID format.")

# ==== Start Command ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_block(update):
        return
    await save_user(update)
    keyboard = [
        [InlineKeyboardButton("💎 Get Premium", callback_data="get_premium")],
        [InlineKeyboardButton("🎥 Demo Channel", url="https://t.me/mmsbhaidemo")],
        [InlineKeyboardButton("✅ Proofs", url="https://t.me/mmsbhaiproof69")]
    ]
    await update.message.reply_photo(photo=START_IMAGE, caption=START_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

# ==== Button Actions ====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_block(update):
        return
    query = update.callback_query
    await query.answer()
    if query.data == "get_premium":
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("🎥 Demo Channel", url="https://t.me/mmsbhaidemo")],
            [InlineKeyboardButton("✅ Proofs", url="https://t.me/mmsbhaiproof69")]
        ]
        await query.edit_message_media(
            media=InputMediaPhoto(PREMIUM_IMAGE, caption=PREMIUM_MESSAGE),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("💎 Get Premium", callback_data="get_premium")],
            [InlineKeyboardButton("🎥 Demo Channel", url="https://t.me/mmsbhaidemo")],
            [InlineKeyboardButton("✅ Proofs", url="https://t.me/mmsbhaiproof69")]
        ]
        await query.edit_message_media(
            media=InputMediaPhoto(START_IMAGE, caption=START_MESSAGE),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==== Broadcast Command ====
# /broadcast command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return await update.message.reply_text("⛔ Only owner can use this command!")

    # Check reply message
    target = update.message.reply_to_message

    # Agar reply nahi kiya, fir /broadcast text se bhej sakte ho
    if not target:
        text = update.message.text
        if text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "").strip()
            if not msg:
                return await update.message.reply_text("⚠️ Broadcast message empty!")
            
            users = users_col.find()
            ok = 0
            fail = 0
            for u in users:
                try:
                    await context.bot.send_message(u["_id"], msg)
                    ok += 1
                except:
                    fail += 1
            return await update.message.reply_text(f"📢 Done\n\n✅ Sent: {ok}\n❌ Failed: {fail}")

        return await update.message.reply_text("Reply to a message or use: /broadcast <text>")

    # ----- MEDIA BROADCAST -----
    users = users_col.find()
    ok = 0
    fail = 0

    for u in users:
        try:
            chat_id = u["_id"]

            # PHOTO
            if target.photo:
                file_id = target.photo[-1].file_id
                await context.bot.send_photo(chat_id, file_id, caption=target.caption or "")

            # VIDEO
            elif target.video:
                await context.bot.send_video(chat_id, target.video.file_id, caption=target.caption or "")

            # DOCUMENT
            elif target.document:
                await context.bot.send_document(chat_id, target.document.file_id, caption=target.caption or "")

            # ANIMATION (GIF)
            elif target.animation:
                await context.bot.send_animation(chat_id, target.animation.file_id, caption=target.caption or "")

            # TEXT
            elif target.text:
                await context.bot.send_message(chat_id, target.text)

            # OTHER TYPES
            else:
                await update.message.reply_text("⚠️ This media type is not supported yet.")

            ok += 1

        except:
            fail += 1

    await update.message.reply_text(f"📢 Broadcast Completed\n\n✅ Sent: {ok}\n❌ Failed: {fail}")


# ==== Stats Command ====
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("⛔ You are not allowed to use this command.")
        return
    total = users_col.count_documents({})
    users = users_col.count_documents({"chat_type": "private"})
    groups = users_col.count_documents({"chat_type": {"$in": ["group", "supergroup"]}})
    premium = users_col.count_documents({"is_premium": True})
    blocked = blocked_col.count_documents({})
    text = (
        "📊 Bot Stats\n\n"
        f"👤 Users: {users}\n"
        f"👥 Groups: {groups}\n"
        f"💎 Premium: {premium}\n"
        f"🚫 Blocked: {blocked}\n"
        f"🔢 Total Saved: {total}"
    )
    await update.message.reply_text(text)

# ==== Premium Command ====
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("⛔ You are not allowed to use this command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /premium <username or user_id>")
        return
    target = context.args[0]
    if target.isdigit():
        query = {"_id": int(target)}
        doc = {"_id": int(target), "is_premium": True}
    else:
        query = {"username": target.lstrip("@")}
        doc = {"username": target.lstrip("@"), "is_premium": True}
    users_col.update_one(query, {"$set": doc}, upsert=True)
    name = target if target.startswith("@") else f"user_id {target}"
    await update.message.reply_text(f"✅ {name} added to Premium List")

# ==== Premium List Command ====
async def premiumlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("⛔ You are not allowed to use this command.")
        return
    premium_users = list(users_col.find({"is_premium": True}))
    if not premium_users:
        await update.message.reply_text("❌ No premium users found.")
        return
    text = f"💎 Premium Users ({len(premium_users)})\n\n"
    for i, user in enumerate(premium_users, start=1):
        if user.get("username"):
            text += f"{i}. @{user['username']}\n"
        else:
            text += f"{i}. {user.get('_id')}\n"
    await update.message.reply_text(text)

# ==== Handle Photo in DM ====
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_block(update):
        return
    await save_user(update)
    chat = update.effective_chat
    if chat.type == "private":
        user = update.effective_user
        username = f"@{user.username}" if user.username else user.full_name
        profile_link = f"[Open Profile](tg://user?id={user.id})"
        text = (
            "📸 New premium user\n\n"
            f"👤 Name: {username}\n"
            f"🔗 Profile: {profile_link}"
        )
        for owner in OWNER_IDS:
            try:
                await update.message.forward(owner)
                await context.bot.send_message(owner, text, parse_mode="Markdown")
            except Exception:
                pass

# ==== Track All Users ====
async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_block(update):
        return
    await save_user(update)

# ==== Main Function ====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("premiumlist", premiumlist))
    app.add_handler(CommandHandler("block", block_user))
    app.add_handler(CommandHandler("unblock", unblock_user))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.ALL, track_users))
    print("Bot started successfully ✅")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
