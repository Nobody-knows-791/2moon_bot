from telegram import User, Chat
import datetime

def mention_html(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{name}</a>'

def build_menu(buttons: list, n_cols: int = 1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(header_buttons, list) else [footer_buttons])
    return menu

async def get_user_info(user: User, chat: Chat = None) -> str:
    text = (
        f"👤 <b>User Info</b>\n"
        f"• Name: {mention_html(user.id, user.first_name)}\n"
        f"• Username: @{user.username if user.username else 'None'}\n"
        f"• ID: <code>{user.id}</code>\n"
    )
    
    if chat and chat.type != "private":
        member = await chat.get_member(user.id)
        join_date = member.joined_date or datetime.datetime.now()
        text += f"• Join Date: {join_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"• Status: {member.status}\n"
    
    return text

def extract_time(time_str: str) -> int:
    if not time_str:
        return None
    try:
        if time_str[-1] == "m":
            return int(time_str[:-1]) * 60
        elif time_str[-1] == "h":
            return int(time_str[:-1]) * 3600
        elif time_str[-1] == "d":
            return int(time_str[:-1]) * 86400
        else:
            return int(time_str)
    except ValueError:
        return None

def format_datetime(dt: datetime.datetime) -> str:
    """Format a datetime object to a string in the format 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')