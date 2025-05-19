from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from utils import is_admin
from database import db

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick a user from the group (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        try:
            await context.bot.ban_chat_member(chat.id, target_user.id)
            await context.bot.unban_chat_member(chat.id, target_user.id)
            await update.message.reply_text(f"👢 *{target_user.first_name} has been kicked!*", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        await update.message.reply_text("Reply to a user's message to kick them!")

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote a user to admin (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        try:
            await context.bot.promote_chat_member(
                chat.id, target_user.id,
                can_delete_messages=True, can_manage_video_chats=True, can_pin_messages=True, can_invite_users=True
            )
            db.add_admin(chat.id, target_user.id)
            await update.message.reply_text(f"🌟 *{target_user.first_name} has been promoted!*", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        await update.message.reply_text("Reply to a user's message to promote them!")

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demote a user from admin (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        try:
            await context.bot.promote_chat_member(chat.id, target_user.id, can_delete_messages=False)
            db.remove_admin(chat.id, target_user.id)
            await update.message.reply_text(f"⬇️ *{target_user.first_name} has been demoted!*", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        await update.message.reply_text("Reply to a user's message to demote them!")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute a user in the group (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        try:
            await context.bot.restrict_chat_member(chat.id, target_user.id, can_send_messages=False)
            await update.message.reply_text(f"🤐 *{target_user.first_name} has been muted!*", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        await update.message.reply_text("Reply to a user's message to mute them!")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warn a user (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        reason = " ".join(context.args) or "No reason provided"
        db.add_warning(chat.id, target_user.id, reason)
        warnings = db.get_warnings(chat.id, target_user.id)
        max_warnings = 3  # Configurable in future
        if len(warnings) >= max_warnings:
            try:
                await context.bot.ban_chat_member(chat.id, target_user.id)
                await update.message.reply_text(
                    f"🔨 *{target_user.first_name} has been banned for reaching {max_warnings} warnings!*",
                    parse_mode="Markdown"
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text(
                f"⚠️ *{target_user.first_name} has been warned ({len(warnings)}/{max_warnings})!* Reason: {reason}",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text("Reply to a user's message to warn them!")

async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom welcome message (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if context.args:
        message = " ".join(context.args)
        db.set_welcome_message(chat.id, message)
        await update.message.reply_text("✅ Welcome message set!", parse_mode="Markdown")
    else:
        await update.message.reply_text("Provide a welcome message (use {first_name} for the user's name).")

async def filter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle filters."""
    chat = update.effective_chat
    message = update.message.text.lower()
    filters = db.get_filters(chat.id)
    for keyword, response in filters.items():
        if keyword.lower() in message:
            await update.message.reply_text(response, parse_mode="Markdown")
            break

async def addfilter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a filter (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if len(context.args) >= 2:
        keyword = context.args[0]
        response = " ".join(context.args[1:])
        db.add_filter(chat.id, keyword, response)
        await update.message.reply_text(f"✅ Filter added for '{keyword}'!", parse_mode="Markdown")
    else:
        await update.message.reply_text("Usage: /addfilter <keyword> <response>")

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retrieve a note."""
    chat = update.effective_chat
    if context.args:
        hashtag = context.args[0]
        note = db.get_note(chat.id, hashtag)
        if note:
            await update.message.reply_text(note, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"No note found for {hashtag}.")
    else:
        await update.message.reply_text("Usage: /note <hashtag>")

async def addnote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a note (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if len(context.args) >= 2:
        hashtag = context.args[0]
        message = " ".join(context.args[1:])
        db.add_note(chat.id, hashtag, message)
        await update.message.reply_text(f"✅ Note added for {hashtag}!", parse_mode="Markdown")
    else:
        await update.message.reply_text("Usage: /addnote <hashtag> <message>")

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lock a feature (admin only)."""
    chat = update.effective_chat
    user = update.effective_user

    if not is_admin(update, context, user.id):
        await update.message.reply_text("🚫 Only admins can use this command!")
        return

    if context.args:
        lock_type = context.args[0].lower()
        valid_locks = ["media", "links", "commands"]
        if lock_type in valid_locks:
            db.set_lock(chat.id, lock_type, True)
            await update.message.reply_text(f"🔒 {lock_type.capitalize()} locked!", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Invalid lock type. Use: {', '.join(valid_locks)}")
    else:
        await update.message.reply_text("Usage: /lock <type> (e.g., media, links, commands)")

def get_admin_handlers():
    """Return admin command handlers."""
    return [
        CommandHandler("kick", kick),
        CommandHandler("promote", promote),
        CommandHandler("demote", demote),
        CommandHandler("mute", mute),
        CommandHandler("warn", warn),
        CommandHandler("setwelcome", setwelcome),
        CommandHandler("addfilter", addfilter),
        CommandHandler("note", note),
        CommandHandler("addnote", addnote),
        CommandHandler("lock", lock),
        MessageHandler(filters.TEXT & ~filters.COMMAND, filter_message),
    ]