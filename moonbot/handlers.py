from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from utils import is_admin, format_welcome_message, owner_keyboard
from database import db
import os

OWNER_ID = int(os.getenv("OWNER_ID"))
SUPPORT_GROUP = int(os.getenv("SUPPORT_GROUP"))

def start(update: Update, context: CallbackContext):
    """Handle /start command."""
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == "private":
        if user.id == OWNER_ID:
            message = (
                f"🌟 *Greetings, Master {user.first_name}!* 🌟\n"
                f"I'm Moon, your loyal bot. Ready to manage groups and spread your commands! 🚀\n"
                f"Use the buttons below to control me:"
            )
            update.message.reply_text(message, parse_mode="Markdown", reply_markup=owner_keyboard())
        else:
            update.message.reply_text(
                f"🌙 *Hey {user.first_name}!* I'm Moon, a group management bot. Add me to your group! 😊",
                parse_mode="Markdown"
            )
    else:
        update.message.reply_text("Please use /start in my DM for setup instructions!")

def welcome_new_member(update: Update, context: CallbackContext):
    """Welcome new members in groups."""
    chat = update.effective_chat
    group = db.get_group(chat.id)
    if group and group.get("welcome_enabled", True):
        for user in update.message.new_chat_members:
            update.message.reply_text(format_welcome_message(user), parse_mode="Markdown")

def ban(update: Update, context: CallbackContext):
    """Ban a user from the group (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        update.message.reply_text("🚫 Only admins can use this command!")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        try:
            context.bot.ban_chat_member(chat.id, target_user.id)
            update.message.reply_text(f"🔨 *{target_user.first_name} has been banned!*", parse_mode="Markdown")
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        update.message.reply_text("Reply to a user's message to ban them!")

def post(update: Update, context: CallbackContext):
    """Owner command to post media/text to groups (in DM)."""
    user = update.effective_user
    if user.id != OWNER_ID:
        update.message.reply_text("🚫 This command is for the owner only!")
        return

    if update.message.reply_to_message:
        # Get the replied message (text or media)
        reply = update.message.reply_to_message
        chat_ids = [SUPPORT_GROUP]  # Add more group IDs dynamically if needed

        for chat_id in chat_ids:
            try:
                if reply.photo:
                    context.bot.send_photo(chat_id, reply.photo[-1].file_id, caption=reply.caption or "")
                elif reply.video:
                    context.bot.send_video(chat_id, reply.video.file_id, caption=reply.caption or "")
                elif reply.document:
                    context.bot.send_document(chat_id, reply.document.file_id, caption=reply.caption or "")
                else:
                    context.bot.send_message(chat_id, reply.text)
                update.message.reply_text(f"📢 Posted to group {chat_id}!")
            except Exception as e:
                update.message.reply_text(f"❌ Error posting to {chat_id}: {str(e)}")
    else:
        update.message.reply_text("Reply to a message or media to post it!")

def callback_query(update: Update, context: CallbackContext):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    user = query.from_user

    if user.id != OWNER_ID:
        query.answer("This is for the owner only!")
        return

    if query.data == "post":
        query.message.reply_text("Reply to a message or media with /post to send it to groups!")
    elif query.data == "settings":
        query.message.reply_text("⚙️ Settings menu (under development).")
    query.answer()

def get_handlers():
    """Return all handlers for the bot."""
    return [
        CommandHandler("start", start),
        CommandHandler("ban", ban),
        CommandHandler("post", post),
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member),
        CallbackQueryHandler(callback_query),
    ]