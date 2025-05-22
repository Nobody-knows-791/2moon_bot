from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler
from config import Config
from database import db
from utils.helpers import mention_html, build_menu
from utils.strings import Strings
import datetime

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    if not chat_member or chat_member.new_chat_member.status not in ["member", "administrator", "creator"]:
        return
    
    user = chat_member.new_chat_member.user
    chat = chat_member.chat
    await db.add_user(user.id, user.username, user.first_name)
    
    welcome_message = await db.get_welcome(chat.id)
    message = welcome_message.format(
        first_name=mention_html(user.id, user.first_name),
        chat_title=chat.title
    )
    
    user_info = (
        f"🌙 <b>Welcome to {chat.title}!</b> 🌙\n\n"
        f"👤 <b>Name:</b> {mention_html(user.id, user.first_name)}\n"
        f"📱 <b>Username:</b> @{user.username if user.username else 'None'}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📅 <b>Join Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"{message}"
    )
    
    buttons = [
        InlineKeyboardButton("📜 Rules", url="https://t.me/RULES_FOR_GROUPS_791/3")
    ]
    
    try:
        profile_photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if profile_photos.photos:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=profile_photos.photos[0][-1].file_id,
                caption=user_info,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([buttons])
            )
        else:
            await context.bot.send_message(
                chat_id=chat.id,
                text=user_info,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([buttons])
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat.id,
            text=user_info,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([buttons])
        )
        await send_error_log(context, Config.OWNER_ID, f"Welcome handler error: {e}")

async def goodbye_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    if not chat_member or chat_member.new_chat_member.status not in ["kicked", "left"]:
        return
    
    user = chat_member.new_chat_member.user
    chat = chat_member.chat
    
    goodbye_message = await db.get_goodbye(chat.id)
    message = goodbye_message.format(
        first_name=mention_html(user.id, user.first_name),
        chat_title=chat.title
    )
    
    user_info = (
        f"👋 <b>Goodbye from {chat.title}!</b> 👋\n\n"
        f"👤 <b>Name:</b> {mention_html(user.id, user.first_name)}\n"
        f"📱 <b>Username:</b> @{user.username if user.username else 'None'}\n"
        f"�ID: <code>{user.id}</code>\n\n"
        f"{message}"
    )
    
    try:
        profile_photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if profile_photos.photos:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=profile_photos.photos[0][-1].file_id,
                caption=user_info,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=chat.id,
                text=user_info,
                parse_mode="HTML"
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat.id,
            text=user_info,
            parse_mode="HTML"
        )
        await send_error_log(context, Config.OWNER_ID, f"Goodbye handler error: {e}")

async def send_error_log(context: ContextTypes.DEFAULT_TYPE, user_id: int, error: str):
    try:
        await context.bot.send_message(
            chat_id=Config.OWNER_ID,
            text=f"⚠️ Error Log:\n\n{error}",
            parse_mode="HTML"
        )
    except:
        pass

welcome_handlers = [
    ChatMemberHandler(welcome_handler, ChatMemberHandler.CHAT_MEMBER),
    ChatMemberHandler(goodbye_handler, ChatMemberHandler.CHAT_MEMBER),
]