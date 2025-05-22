from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import Config
from database import db
from utils.helpers import build_menu, get_user_info
from utils.strings import Strings

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    await db.add_user(user.id, user.username, user.first_name)
    
    buttons = [
        InlineKeyboardButton(
            "➕ Add to Group", 
            url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users"
        ),
        InlineKeyboardButton("🚀 Support", url=Config.SUPPORT_CHAT_LINK),
        InlineKeyboardButton("📢 Channel", url="https://t.me/chilling_friends_support"),
        InlineKeyboardButton("📜 Commands", callback_data="user_commands"),
    ]
    
    caption = (
        f"🌙 <b>Welcome to {Config.BOT_NAME}!</b> 🌙\n\n"
        f"I'm your ultimate group management bot, packed with powerful features to keep your chats organized and fun!\n\n"
        f"👉 <b>Add me to your group</b> to unlock moderation tools, custom welcomes, filters, and more!\n"
        f"👉 Join our <b>support group</b> for updates and help.\n"
        f"👉 Check out my <b>commands</b> to get started!"
    )
    
    if user.id == Config.OWNER_ID and chat.type == "private":
        buttons.append(InlineKeyboardButton("👑 Owner Panel", callback_data="owner_panel"))
    
    try:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=Config.BOT_PHOTO,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
            parse_mode="HTML"
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"Error sending photo: {e}\n\n{caption}",
            reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
            parse_mode="HTML"
        )
        await send_error_log(context, user.id, f"Start command photo error: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type != "private":
        buttons = [
            InlineKeyboardButton("📜 View Commands in DM", url=f"https://t.me/{Config.BOT_USERNAME}?start=help")
        ]
        await update.message.reply_text(
            "Please use /help in my DM to view all commands!",
            reply_markup=InlineKeyboardMarkup([buttons])
        )
        return
    
    await update.message.reply_text(
        Strings.HELP_MESSAGE,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
        ])
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    try:
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif len(context.args) > 0:
            target_user = await context.bot.get_chat(context.args[0])
        else:
            target_user = update.effective_user
        
        user_info = await get_user_info(target_user, chat if chat.type != "private" else None)
        profile_photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
        
        if profile_photos.photos:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=profile_photos.photos[0][-1].file_id,
                caption=user_info,
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(user_info, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Error getting user info: {e}")
        await send_error_log(context, update.effective_user.id, f"Info command error: {e}")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"🆔 <b>Chat ID:</b> <code>{update.effective_chat.id}</code>"
    if update.effective_chat.type != "private":
        text += f"\n👥 <b>Title:</b> {update.effective_chat.title}"
    
    if update.message.reply_to_message:
        text += f"\n\n👤 <b>User ID:</b> <code>{update.message.reply_to_message.from_user.id}</code>"
        if update.message.reply_to_message.from_user.username:
            text += f"\n📱 <b>Username:</b> @{update.message.reply_to_message.from_user.username}"
    
    await update.message.reply_text(text, parse_mode="HTML")

async def admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text("This command can only be used in groups!")
        return
    
    try:
        admins = await chat.get_administrators()
        admin_list = [f"• {mention_html(admin.user.id, admin.user.first_name)}" for admin in admins if not admin.user.is_bot]
        await update.message.reply_text(
            f"👮‍♂️ <b>Admins in {chat.title}</b> 👮‍♂️\n\n{'\n'.join(admin_list)}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching admins: {e}")
        await send_error_log(context, update.effective_user.id, f"Admins command error: {e}")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! I'm alive and ready to assist!")

async def user_commands_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        Strings.HELP_MESSAGE,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
        ])
    )

async def user_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = [
        InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start"),
    ]
    
    await query.edit_message_text(
        "⚙️ <b>User Settings</b>\n\n"
        "No settings available yet.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([buttons])
    )

async def back_to_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = [
        InlineKeyboardButton(
            "➕ Add to Group", 
            url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users"
        ),
        InlineKeyboardButton("🚀 Support", url=Config.SUPPORT_CHAT_LINK),
        InlineKeyboardButton("📢 Channel", url="https://t.me/chilling_friends_support"),
        InlineKeyboardButton("📜 Commands", callback_data="user_commands"),
    ]
    
    if update.effective_user.id == Config.OWNER_ID and update.effective_chat.type == "private":
        buttons.append(InlineKeyboardButton("👑 Owner Panel", callback_data="owner_panel"))
    
    caption = (
        f"🌙 <b>Welcome to {Config.BOT_NAME}!</b> 🌙\n\n"
        f"I'm your ultimate group management bot, packed with powerful features to keep your chats organized and fun!\n\n"
        f"👉 <b>Add me to your group</b> to unlock moderation tools, custom welcomes, filters, and more!\n"
        f"👉 Join our <b>support group</b> for updates and help.\n"
        f"👉 Check out my <b>commands</b> to get started!"
    )
    
    await query.edit_message_text(
        caption,
        reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
        parse_mode="HTML"
    )

async def owner_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id != Config.OWNER_ID:
        await query.edit_message_text("⚠️ This command is only for the bot owner.")
        return
    
    if update.effective_chat.type != "private":
        await query.edit_message_text("⚠️ Owner panel is only available in DMs.")
        return
    
    buttons = [
        InlineKeyboardButton("📊 Stats", callback_data="owner_stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="owner_broadcast"),
        InlineKeyboardButton("🚫 GBan User", callback_data="owner_gban"),
        InlineKeyboardButton("📝 Post to Groups", callback_data="owner_post"),
        InlineKeyboardButton("🔄 Update Bot", callback_data="owner_update"),
        InlineKeyboardButton("📜 Logs", callback_data="owner_logs"),
        InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start"),
    ]
    
    await query.edit_message_text(
        f"👑 <b>Owner Panel - {Config.BOT_NAME}</b> 👑\n\n"
        "You have access to special owner commands:",
        reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
        parse_mode="HTML"
    )

async def send_error_log(context: ContextTypes.DEFAULT_TYPE, user_id: int, error: str):
    if user_id == Config.OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=Config.OWNER_ID,
                text=f"⚠️ Error Log:\n\n{error}",
                parse_mode="HTML"
            )
        except:
            pass

user_handlers = [
    CommandHandler("start", start_command),
    CommandHandler("help", help_command),
    CommandHandler("info", info_command),
    CommandHandler("id", id_command),
    CommandHandler("admins", admins_command),
    CommandHandler("ping", ping_command),
    CallbackQueryHandler(user_commands_callback, pattern="^user_commands$"),
    CallbackQueryHandler(user_settings_callback, pattern="^user_settings$"),
    CallbackQueryHandler(back_to_start_callback, pattern="^back_to_start$"),
    CallbackQueryHandler(owner_panel_callback, pattern="^owner_panel$"),
]