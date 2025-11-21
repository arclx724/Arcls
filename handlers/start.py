# ============================================================
# Group Manager Bot
# Author: learningbots79 (https://github.com/learningbots79) 
# Support: https://t.me/learning_bots
# Channel: https://t.me/learningbots79
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from datetime import datetime, timedelta
from config import BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID
import db

# ==========================================================
# 24-Hour Ban Tracking System
# ==========================================================

admin_ban_data = {}   # admin_id → {count, start_time}
MAX_BANS = 10         # Max bans allowed in 24 hours


def register_ban(admin_id):
    now = datetime.now()

    if admin_id not in admin_ban_data:
        admin_ban_data[admin_id] = {"count": 1, "start": now}
        return 1

    data = admin_ban_data[admin_id]

    # Reset after 24 hrs
    if now - data["start"] > timedelta(hours=24):
        admin_ban_data[admin_id] = {"count": 1, "start": now}
        return 1

    data["count"] += 1
    return data["count"]


async def check_and_demote(client, chat_id, admin_id):
    count = register_ban(admin_id)

    if count > MAX_BANS:
        # Auto-demote abusive admin
        try:
            await client.promote_chat_member(
                chat_id,
                admin_id,
                can_manage_chat=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_manage_video_chats=False,
                can_promote_members=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_change_info=False,
            )

            await client.send_message(
                chat_id,
                f"⚠️ **Auto-Protection Enabled**\n\n"
                f"Admin [{admin_id}](tg://user?id={admin_id}) ne "
                f"**24 hours me 10 se zyada members ban/remove** kiye.\n"
                f"Isliye unko automatically **DEMOTE** kar diya gaya."
            )
        except Exception as e:
            print("Demote Error:", e)


# ==========================================================
# Detect ANY Ban/Kick done by Admin or Bot
# ==========================================================

def register_handlers(app: Client):

    @app.on_chat_member_updated()
    async def detect_ban_events(client, event):
        try:
            old = event.old_chat_member
            new = event.new_chat_member

            # Detect ban/kick
            if new.status == "kicked":
                admin_id = event.from_user.id  # Who banned the user
                chat_id = event.chat.id

                # Ignore bot's own bans
                if admin_id == client.me.id:
                    return

                await check_and_demote(client, chat_id, admin_id)

        except Exception as e:
            print("Ban detection error:", e)

# ==========================================================
# Start Menu
# ==========================================================
    async def send_start_menu(message, user):
        text = f"""

   ✨ Hello {user}! ✨

👋 I am Nomad 🤖 

Highlights:
─────────────────────────────
- Smart Anti-Spam & Link Shield
- Adaptive Lock System (URLs, Media, Language & more)
- Modular & Scalable Protection
- Sleek UI with Inline Controls

» More New Features coming soon ...
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚒️ Add to Group ⚒️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("⌂ Support ⌂", url=SUPPORT_GROUP),
                InlineKeyboardButton("⌂ Update ⌂", url=UPDATE_CHANNEL),
            ],
            [
                InlineKeyboardButton("※ ŎŴɳēŔ ※", user_id=OWNER_ID)
            ],
            [InlineKeyboardButton("📚 Help Commands 📚", callback_data="help")]
        ])

        if message.text:
            await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons)
        else:
            media = InputMediaPhoto(media=START_IMAGE, caption=text)
            await message.edit_media(media=media, reply_markup=buttons)

# ==========================================================
# Start Command
# ==========================================================
    @app.on_message(filters.private & filters.command("start"))
    async def start_command(client, message):
        user = message.from_user
        await db.add_user(user.id, user.first_name)
        await send_start_menu(message, user.first_name)

# ==========================================================
# Help Menu
# ==========================================================
    async def send_help_menu(message):
        text = """
╔══════════════════╗
     Help Menu
╚══════════════════╝

Choose a category below to explore commands:
─────────────────────────────
"""
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⌂ Greetings ⌂", callback_data="greetings"),
                InlineKeyboardButton("⌂ Locks ⌂", callback_data="locks"),
            ],
            [
                InlineKeyboardButton("⌂ Moderation ⌂", callback_data="moderation")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
        ])

        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await message.edit_media(media=media, reply_markup=buttons)

# ==========================================================
# Help Callback
# ==========================================================
    @app.on_callback_query(filters.regex("help"))
    async def help_callback(client, callback_query):
        await send_help_menu(callback_query.message)
        await callback_query.answer()

# ==========================================================
# Back to Start
# ==========================================================
    @app.on_callback_query(filters.regex("back_to_start"))
    async def back_to_start_callback(client, callback_query):
        user = callback_query.from_user.first_name
        await send_start_menu(callback_query.message, user)
        await callback_query.answer()

# ==========================================================
# Greetings
# ==========================================================
    @app.on_callback_query(filters.regex("greetings"))
    async def greetings_callback(client, callback_query):
        text = """
╔══════════════════╗
    ⚙ Welcome System
╚══════════════════╝

Commands:
- /setwelcome <text>
- /welcome on
- /welcome off

Placeholders:
{username}, {first_name}, {id}, {mention}
"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ])
        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()

# ==========================================================
# Locks
# ==========================================================
    @app.on_callback_query(filters.regex("locks"))
    async def locks_callback(client, callback_query):
        text = """
╔══════════════════╗
     ⚙ Locks System
╚══════════════════╝

- /lock <type>
- /unlock <type>
- /locks

Types: url, sticker, media, username, language
"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ])
        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()

# ==========================================================
# Moderation
# ==========================================================
    @app.on_callback_query(filters.regex("moderation"))
    async def info_callback(client, callback_query):
        try:
            text = """
╔══════════════════╗
      ⚙️ Moderation System
╚══════════════════╝

¤ /kick
¤ /ban
¤ /unban
¤ /mute
¤ /unmute
¤ /warn
¤ /warns
¤ /resetwarns
¤ /promote
¤ /demote
"""
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
    
            media = InputMediaPhoto(media=START_IMAGE, caption=text)
            await callback_query.message.edit_media(media=media, reply_markup=buttons)
            await callback_query.answer()
    
        except Exception as e:
            print("Error:", e)
            await callback_query.answer("❌ Error occurred.", show_alert=True)

# ==========================================================
# Broadcast
# ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_message(client, message):
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to broadcast.")

        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Only owner can use this.")

        text_to_send = message.reply_to_message.text or message.reply_to_message.caption
        users = await db.get_all_users()
        sent, failed = 0, 0

        await message.reply_text(f"Broadcasting to {len(users)} users...")

        for user_id in users:
            try:
                await client.send_message(user_id, text_to_send)
                sent += 1
            except:
                failed += 1

        await message.reply_text(f"Done!\nSent: {sent}\nFailed: {failed}")

# ==========================================================
# Stats
# ==========================================================
    @app.on_message(filters.private & filters.command("stats"))
    async def stats_command(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Only owner can use this.")

        users = await db.get_all_users()
        return await message.reply_text(f"💡 Total users: {len(users)}")
