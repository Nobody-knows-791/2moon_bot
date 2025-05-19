from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import db
import os

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu (owner only)."""
    user = update.effective_user
    if user.id != int(os.getenv("OWNER_ID")):
        await update.message.reply_text("🚫 This command is for the owner only!")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("🔄 Restart", callback_data="restart")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("🔧 Group Settings", callback_data="group_settings")]
    ]
    await update.message.reply_text(
        "⚙️ *Settings Menu* ⚙️\nChoose an option:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot usage stats (owner only)."""
    query = update.callback_query
    user = query.from_user
    if user.id != int(os.getenv("OWNER_ID")):
        await query.answer("This is for the owner only!")
        return

    group_count = db.groups.count_documents({})
    user_count = db.users.count_documents({})
    message = (
        f"📊 *Bot Stats* 📊\n"
        f"Groups: {group_count}\n"
        f"Users: {user_count}"
    )
    await query.message.reply_text(message, parse_mode="Markdown")
    await query.answer()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart the bot (owner only)."""
    query = update.callback_query
    user = query.from_user
    if user.id != int(os.getenv("OWNER_ID")):
        await query.answer("This is for the owner only!")
        return

    await query.message.reply_text("🔄 Restarting bot...", parse_mode="Markdown")
    await query.answer()
    os._exit(0)  # Note: Requires proper deployment setup to restart

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alternative broadcast command (owner only)."""
    query = update.callback_query
    user = query.from_user
    if user.id != int(os.getenv("OWNER_ID")):
        await query.answer("This is for the owner only!")
        return

    await query.message.reply_text("Reply to a message or media with /post to broadcast!", parse_mode="Markdown")
    await query.answer()

async def group_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage group settings (owner only)."""
    query = update.callback_query
    user = query.from_user
    if user.id != int(os.getenv("OWNER_ID")):
        await query.answer("This is for the owner only!")
        return

    await query.message.reply_text("🔧 Group settings (under development).", parse_mode="Markdown")
    await query.answer()

def get_settings_handlers():
    """Return settings handlers."""
    return [
        CommandHandler("settings", settings),
        CallbackQueryHandler(stats, pattern="stats"),
        CallbackQueryHandler(restart, pattern="restart"),
        CallbackQueryHandler(broadcast, pattern="broadcast"),
        CallbackQueryHandler(group_settings, pattern="group_settings"),
    ]