from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import os
from utils import is_admin, format_welcome_message, format_info_message, start_keyboard
from database import db

OWNER_ID = int(os.getenv("OWNER_ID"))
SUPPORT_GROUP = int(os.getenv("SUPPORT_GROUP"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == "private":
        # Send bot's profile picture
        bot = context.bot
        photos = await bot.get_user_profile_photos(bot.id, limit=1)
        message = (
            f"🌟 *Greetings, {user.first_name}!* 🌟\n"
            f"I'm Moon, your group management bot! Ready to keep things awesome! 🚀\n"
            f"Use the buttons below to get started:"
        )
        if photos.photos:
            await update.message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=message,
                parse_mode="Markdown",
                reply_markup=start_keyboard()
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode="Markdown",
                reply_markup=start_keyboard()
            )
    else:
        await update.message.reply_text("Please use /start in my DM for setup instructions!")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome new members in groups."""
    chat = update.effective_chat
    group = db.get_group(chat.id)
    if group and group.get("welcome_enabled", True):
        for user in update.message.new_chat_members:
            if group.get("welcome_message"):
                # Custom welcome message
                message = group["welcome_message"].replace("{first_name}", user.first_name)
                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                # Default welcome with profile picture
                photos = await user.get_profile_photos(limit=1)
                message = format_welcome_message(user, chat.id)
                try:
                    if photos.photos:
                        await update.message.reply_photo(
                            photo=photos.photos[0][-1].file_id,
                            caption=message,
                            parse_mode="MarkdownV2"
                        )
                    else:
                        await update.message.reply_text(message, parse_mode="MarkdownV2")
                except Exception as e:
                    await update.message.reply_text(f"Error sending welcome: {str(e)}")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user info like Rose Bot."""
    chat = update.effective_chat
    user = update.effective_user

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        target_user = user

    photos = await target_user.get_profile_photos(limit=1)
    message = format_info_message(target_user)
    try:
        if photos.photos:
            await update.message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=message,
                parse_mode="MarkdownV2"
            )
        else:
            await update.message.reply_text(message, parse_mode="MarkdownV2")
    except Exception as e:
        await update.message.reply_text(f"Error sending info: {str(e)}")

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to post media/text to all groups."""
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("🚫 This command is for the owner only!")
        return

    if update.message.reply_to_message:
        reply = update.message.reply_to_message
        # Get all groups from MongoDB
        groups = db.groups.find()
        chat_ids = [group["group_id"] for group in groups]

        for chat_id in chat_ids:
            try:
                if reply.photo:
                    await context.bot.send_photo(chat_id, reply.photo[-1].file_id, caption=reply.caption or "")
                elif reply.video:
                    await context.bot.send_video(chat_id, reply.video.file_id, caption=reply.caption or "")
                elif reply.document:
                    await context.bot.send_document(chat_id, reply.document.file_id, caption=reply.caption or "")
                else:
                    await context.bot.send_message(chat_id, reply.text)
                await update.message.reply_text(f"📢 Posted to group {chat_id}!")
            except Exception as e:
                await update.message.reply_text(f"❌ Error posting to {chat_id}: {str(e)}")
    else:
        await update.message.reply_text("Reply to a message or media to post it!")

async def callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    user = query.from_user

    if query.data == "commands":
        commands = (
            "📜 *Available Commands*\n"
            "/start - Start the bot\n"
            "/info - Get user info\n"
            "/ban - Ban a user (admin only)"
        )
        if user.id == OWNER_ID:
            commands += "\n/post - Post to groups\n/stats - Bot stats\n/restart - Restart bot"
        await query.message.reply_text(commands, parse_mode="Markdown")
    elif query.data == "post" and user.id == OWNER_ID:
        await query.message.reply_text("Reply to a message or media with /post to send it to groups!")
    elif query.data == "settings" and user.id == OWNER_ID:
        await query.message.reply_text("⚙️ Settings menu (use /settings for full options).")
    else:
        await query.answer("This is for the owner only!")
        return
    await query.answer()

def get_handlers():
    """Return all handlers for the bot."""
    return [
        CommandHandler("start", start),
        CommandHandler("info", info),
        CommandHandler("post", post),
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member),
        CallbackQueryHandler(callback_query),
    ]