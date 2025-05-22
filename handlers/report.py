from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from config import Config
from utils.decorators import group_only
from utils.helpers import mention_html

@group_only
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user
    chat = update.effective_chat
    
    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to report it.")
        return
    
    reported_message = message.reply_to_message
    reported_user = reported_message.from_user
    
    admins = await chat.get_administrators()
    admin_mentions = [mention_html(admin.user.id, admin.user.first_name) for admin in admins if not admin.user.is_bot]
    
    buttons = [
        InlineKeyboardButton("🔗 View Message", url=f"https://t.me/c/{str(chat.id)[4:]}/{reported_message.message_id}")
    ]
    
    await message.reply_text(
        f"🚨 {mention_html(user.id, user.first_name)} reported a message from "
        f"{mention_html(reported_user.id, reported_user.first_name)}.\n\n"
        f"Admins: {' '.join(admin_mentions)}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([buttons])
    )

report_handlers = [
    CommandHandler("report", report_command),
]