from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, filters
from config import Config
from database import db
from utils.decorators import owner_only
from utils.helpers import format_datetime, build_menu
from utils.strings import Strings
import uuid

@owner_only
async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type != "private":
        await update.message.reply_text("⚠️ Owner panel is only available in DMs. Use /start in my DM.")
        return
    
    buttons = [
        InlineKeyboardButton("📊 Stats", callback_data="owner_stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="owner_broadcast"),
        InlineKeyboardButton("🚫 GBan User", callback_data="owner_gban"),
        InlineKeyboardButton("📝 Post to Groups", callback_data="owner_post"),
        InlineKeyboardButton("🔄 Update Bot", callback_data="owner_update"),
        InlineKeyboardButton("📜 Logs", callback_data="owner_logs"),
    ]
    
    try:
        await update.message.reply_text(
            f"👑 <b>Owner Panel - {Config.BOT_NAME}</b> 👑\n\n"
            f"Welcome back, {user.first_name}!\n\n"
            "You have access to special owner commands:",
            reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error displaying owner panel: {e}")
        await send_error_log(context, user.id, f"Owner start error: {e}")

@owner_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_count = await db.get_chat_count()
        user_count = await db.get_user_count()
        gban_count = await db.gbans.count_documents({})
        chats = await db.get_all_chats()
        
        chat_info = "\n".join([
            f"• {chat['chat_title']} (ID: {chat['chat_id']})" + 
            (f" Link: t.me/{chat['chat_title'].replace(' ', '')}" if not chat.get('is_private', True) else "")
            for chat in chats
        ])
        
        await update.message.reply_text(
            f"📊 <b>Bot Statistics</b>\n\n"
            f"• Groups: <code>{chat_count}</code>\n"
            f"• Users: <code>{user_count}</code>\n"
            f"• GBanned Users: <code>{gban_count}</code>\n\n"
            f"<b>Groups:</b>\n{chat_info}\n\n"
            f"<b>Version:</b> 1.0.0",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching stats: {e}")
        await send_error_log(context, update.effective_user.id, f"Stats command error: {e}")

@owner_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to broadcast it.")
        return
    
    buttons = [
        InlineKeyboardButton("✅ Confirm Broadcast", callback_data=f"confirm_broadcast_{uuid.uuid4()}"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast"),
    ]
    
    try:
        await update.message.reply_text(
            f"📢 <b>Broadcast Preview</b>\n\n"
            f"Are you sure you want to broadcast this message to all users and groups?",
            reply_markup=InlineKeyboardMarkup([buttons]),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error initiating broadcast: {e}")
        await send_error_log(context, update.effective_user.id, f"Broadcast command error: {e}")

@owner_only
async def gban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /gban <user_id> <reason>")
        return
    
    try:
        user_id = int(context.args[0])
        reason = " ".join(context.args[1:])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return
    
    try:
        user = await db.get_user(user_id)
        if not user:
            await update.message.reply_text("User not found in database.")
            return
        
        await db.add_gban(user_id, reason, update.effective_user.id)
        
        chats = await db.get_all_chats()
        for chat in chats:
            try:
                await context.bot.ban_chat_member(chat["chat_id"], user_id)
            except:
                continue
        
        await update.message.reply_text(
            f"🚫 User <code>{user_id}</code> has been globally banned.\n"
            f"📝 Reason: <code>{reason}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error in gban: {e}")
        await send_error_log(context, update.effective_user.id, f"Gban command error: {e}")

@owner_only
async def ungban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /ungban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return
    
    try:
        await db.remove_gban(user_id)
        
        chats = await db.get_all_chats()
        for chat in chats:
            try:
                await context.bot.unban_chat_member(chat["chat_id"], user_id)
            except:
                continue
        
        await update.message.reply_text(
            f"✅ User <code>{user_id}</code> has been removed from global ban list.",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error in ungban: {e}")
        await send_error_log(context, update.effective_user.id, f"Ungban command error: {e}")

@owner_only
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chats = await context.bot.get_updates()
        for update in chats:
            if update.my_chat_member:
                chat = update.my_chat_member.chat
                is_private = chat.type == "private" or not hasattr(chat, 'username') or not chat.username
                await db.add_chat(chat.id, chat.title, is_private)
        
        await update.message.reply_text("🔄 Bot data updated successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error updating bot data: {e}")
        await send_error_log(context, update.effective_user.id, f"Update command error: {e}")

@owner_only
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Logs are sent to your DM when errors occur.")

async def owner_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        chat_count = await db.get_chat_count()
        user_count = await db.get_user_count()
        gban_count = await db.gbans.count_documents({})
        chats = await db.get_all_chats()
        
        chat_info = "\n".join([
            f"• {chat['chat_title']} (ID: {chat['chat_id']})" + 
            (f" Link: t.me/{chat['chat_title'].replace(' ', '')}" if not chat.get('is_private', True) else "")
            for chat in chats
        ])
        
        await query.edit_message_text(
            f"📊 <b>Bot Statistics</b>\n\n"
            f"• Groups: <code>{chat_count}</code>\n"
            f"• Users: <code>{user_count}</code>\n"
            f"• GBanned Users: <code>{gban_count}</code>\n\n"
            f"<b>Groups:</b>\n{chat_info}\n\n"
            f"<b>Version:</b> 1.0.0",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
            ])
        )
    except Exception as e:
        await query.edit_message_text(f"Error fetching stats: {e}")
        await send_error_log(context, update.effective_user.id, f"Owner stats callback error: {e}")

async def owner_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not query.message.reply_to_message:
        await query.edit_message_text("Error: Original message not found.")
        return
    
    original_message = query.message.reply_to_message
    users = await db.get_all_users()
    chats = await db.get_all_chats()
    
    success_users = 0
    failed_users = 0
    success_chats = 0
    failed_chats = 0
    
    try:
        for user in users:
            try:
                await context.bot.copy_message(
                    chat_id=user["user_id"],
                    from_chat_id=original_message.chat_id,
                    message_id=original_message.message_id
                )
                success_users += 1
            except:
                failed_users += 1
        
        for chat in chats:
            try:
                await context.bot.copy_message(
                    chat_id=chat["chat_id"],
                    from_chat_id=original_message.chat_id,
                    message_id=original_message.message_id
                )
                success_chats += 1
            except:
                failed_chats += 1
        
        await query.edit_message_text(
            f"📢 <b>Broadcast Results</b>\n\n"
            f"<u>Users</u>\n"
            f"✅ Success: <code>{success_users}</code>\n"
            f"❌ Failed: <code>{failed_users}</code>\n\n"
            f"<u>Groups</u>\n"
            f"✅ Success: <code>{success_chats}</code>\n"
            f"❌ Failed: <code>{failed_chats}</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
            ])
        )
    except Exception as e:
        await query.edit_message_text(f"Error broadcasting: {e}")
        await send_error_log(context, update.effective_user.id, f"Broadcast callback error: {e}")

async def owner_gban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🚫 Please use /gban <user_id> <reason> to globally ban a user.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
        ])
    )

async def owner_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📝 Please use /post by replying to a message to post to all groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
        ])
    )

async def owner_update_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        chats = await context.bot.get_updates()
        for update in chats:
            if update.my_chat_member:
                chat = update.my_chat_member.chat
                is_private = chat.type == "private" or not hasattr(chat, 'username') or not chat.username
                await db.add_chat(chat.id, chat.title, is_private)
        
        await query.edit_message_text(
            "🔄 Bot data updated successfully!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
            ])
        )
    except Exception as e:
        await query.edit_message_text(f"Error updating bot data: {e}")
        await send_error_log(context, update.effective_user.id, f"Update callback error: {e}")

async def owner_logs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📜 Logs are sent to your DM when errors occur.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
        ])
    )

async def owner_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = [
        InlineKeyboardButton("📊 Stats", callback_data="owner_stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="owner_broadcast"),
        InlineKeyboardButton("🚫 GBan User", callback_data="owner_gban"),
        InlineKeyboardButton("📝 Post to Groups", callback_data="owner_post"),
        InlineKeyboardButton("🔄 Update Bot", callback_data="owner_update"),
        InlineKeyboardButton("📜 Logs", callback_data="owner_logs"),
    ]
    
    try:
        await query.edit_message_text(
            f"👑 <b>Owner Panel - {Config.BOT_NAME}</b> 👑\n\n"
            "You have access to special owner commands:",
            reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
            parse_mode="HTML"
        )
    except Exception as e:
        await query.edit_message_text(f"Error returning to owner panel: {e}")
        await send_error_log(context, update.effective_user.id, f"Owner back callback error: {e}")

async def cancel_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Broadcast cancelled.")

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

admin_handlers = [
    CommandHandler("start", owner_start, filters=filters.User(Config.OWNER_ID)),
    CommandHandler("stats", stats_command, filters=filters.User(Config.OWNER_ID)),
    CommandHandler("broadcast", broadcast_command, filters=filters.User(Config.OWNER_ID)),
    CommandHandler("gban", gban_command, filters=filters.User(Config.OWNER_ID)),
    CommandHandler("ungban", ungban_command, filters=filters.User(Config.OWNER_ID)),
    CommandHandler("update", update_command, filters=filters.User(Config.OWNER_ID)),
    CommandHandler("logs", logs_command, filters=filters.User(Config.OWNER_ID)),
    CallbackQueryHandler(owner_stats_callback, pattern="^owner_stats$"),
    CallbackQueryHandler(owner_broadcast_callback, pattern="^owner_broadcast$"),
    CallbackQueryHandler(owner_gban_callback, pattern="^owner_gban$"),
    CallbackQueryHandler(owner_post_callback, pattern="^owner_post$"),
    CallbackQueryHandler(owner_update_callback, pattern="^owner_update$"),
    CallbackQueryHandler(owner_logs_callback, pattern="^owner_logs$"),
    CallbackQueryHandler(owner_back_callback, pattern="^owner_back$"),
    CallbackQueryHandler(cancel_broadcast_callback, pattern="^cancel_broadcast$"),
    CallbackQueryHandler(owner_broadcast_callback, pattern="^confirm_broadcast_.*$"),
]