from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, filters
from telegram import ChatPermissions
from config import Config
from database import db
from utils.decorators import admin_only, group_only
from utils.helpers import mention_html

@group_only
@admin_only
async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text(
            "Usage: /lock <type>\nTypes: messages, media, stickers, polls, links, bots"
        )
        return
    
    lock_type = context.args[0].lower()
    chat = update.effective_chat
    
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_send_polls=True,
        can_invite_users=True,
        can_pin_messages=True,
        can_change_info=True
    )
    
    if lock_type == "messages":
        permissions.can_send_messages = False
    elif lock_type == "media":
        permissions.can_send_media_messages = False
    elif lock_type == "stickers":
        permissions.can_send_other_messages = False
    elif lock_type == "polls":
        permissions.can_send_polls = False
    elif lock_type == "links":
        permissions.can_add_web_page_previews = False
    elif lock_type == "bots":
        permissions.can_invite_users = False
    else:
        await update.message.reply_text("Invalid lock type. Use: messages, media, stickers, polls, links, bots")
        return
    
    try:
        await chat.set_permissions(permissions)
        await update.message.reply_text(f"🔒 {lock_type.capitalize()} locked for non-admins.")
    except Exception as e:
        await update.message.reply_text(f"Failed to lock {lock_type}: {e}")

@group_only
@admin_only
async def unlock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text(
            "Usage: /unlock <type>\nTypes: messages, media, stickers, polls, links, bots"
        )
        return
    
    lock_type = context.args[0].lower()
    chat = update.effective_chat
    
    permissions = await chat.get_permissions()
    if not permissions:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_change_info=True
        )
    
    if lock_type == "messages":
        permissions.can_send_messages = True
    elif lock_type == "media":
        permissions.can_send_media_messages = True
    elif lock_type == "stickers":
        permissions.can_send_other_messages = True
    elif lock_type == "polls":
        permissions.can_send_polls = True
    elif lock_type == "links":
        permissions.can_add_web_page_previews = True
    elif lock_type == "bots":
        permissions.can_invite_users = True
    else:
        await update.message.reply_text("Invalid unlock type. Use: messages, media, stickers, polls, links, bots")
        return
    
    try:
        await chat.set_permissions(permissions)
        await update.message.reply_text(f"🔓 {lock_type.capitalize()} unlocked for non-admins.")
    except Exception as e:
        await update.message.reply_text(f"Failed to unlock {lock_type}: {e}")

@group_only
@admin_only
async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /promote <user> or reply to a message with /promote")
        return
    
    chat = update.effective_chat
    user = update.effective_user
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
        except:
            await update.message.reply_text("User not found.")
            return
    
    if target_user.id == context.bot.id:
        await update.message.reply_text("I can't promote myself!")
        return
    
    try:
        await chat.promote_member(
            target_user.id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_invite_users=True
        )
        await update.message.reply_text(
            f"👤 {mention_html(target_user.id, target_user.first_name)} has been promoted to admin.",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to promote user: {e}")

@group_only
@admin_only
async def demote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /demote <user> or reply to a message with /demote")
        return
    
    chat = update.effective_chat
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
        except:
            await update.message.reply_text("User not found.")
            return
    
    try:
        await chat.promote_member(
            target_user.id,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_invite_users=False
        )
        await update.message.reply_text(
            f"👤 {mention_html(target_user.id, target_user.first_name)} has been demoted from admin.",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to demote user: {e}")

@group_only
@admin_only
async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to start purging from there.")
        return
    
    chat = update.effective_chat
    start_message_id = update.message.reply_to_message.message_id
    end_message_id = update.message.message_id
    
    try:
        for msg_id in range(start_message_id, end_message_id + 1):
            try:
                await context.bot.delete_message(chat.id, msg_id)
            except:
                continue
        await update.message.reply_text("🧹 Messages purged successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to purge messages: {e}")

moderation_handlers = [
    CommandHandler("lock", lock_command),
    CommandHandler("unlock", unlock_command),
    CommandHandler("promote", promote_command),
    CommandHandler("demote", demote_command),
    CommandHandler("purge", purge_command),
]