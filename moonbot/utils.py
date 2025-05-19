from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def is_admin(update, context, user_id):
    """Check if a user is an admin in the chat."""
    chat = update.effective_chat
    try:
        admins = context.bot.get_chat_administrators(chat.id)
        return any(admin.user.id == user_id for admin in admins)
    except:
        return False

def escape_markdown_v2(text):
    """Escape special characters for MarkdownV2."""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in special_chars else char for char in text)

def format_welcome_message(user, chat_id):
    """Format a default welcome message with user details."""
    username = f"@{escape_markdown_v2(user.username)}" if user.username else "No username"
    first_name = escape_markdown_v2(user.first_name)
    profile_link = f"tg://user?id={user.id}"
    return (
        f"🌙 *Welcome, [{first_name}]({profile_link})!* 🌙\n"
        f"Username: {username}\n"
        f"User ID: `{user.id}`\n"
        f"Enjoy your stay in our group\\! Follow the rules\\! 😎"
    )

def format_info_message(user):
    """Format user info like Rose Bot."""
    username = f"@{escape_markdown_v2(user.username)}" if user.username else "No username"
    first_name = escape_markdown_v2(user.first_name)
    return (
        f"🌟 *User Info* 🌟\n"
        f"Name: {first_name}\n"
        f"Username: {username}\n"
        f"ID: `{user.id}`\n"
        f"Profile: [View](tg://user?id={user.id})"
    )

def owner_keyboard():
    """Create an inline keyboard for owner commands."""
    keyboard = [
        [InlineKeyboardButton("📢 Post to Groups", callback_data="post")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def start_keyboard():
    """Create an inline keyboard for /start in DM."""
    keyboard = [
        [InlineKeyboardButton("➕ Add to Group", url="https://t.me/moon_791_bot?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")],
        [InlineKeyboardButton("📨 Support Group", url="https://t.me/+LAyiWUO6h84wM2Fl")],
        [InlineKeyboardButton("📜 Commands", callback_data="commands")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)