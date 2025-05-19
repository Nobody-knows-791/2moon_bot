import os
import asyncio
import signal
from telegram.ext import Application
from dotenv import load_dotenv
from handlers import get_handlers
from admin_handlers import get_admin_handlers
from settings_handlers import get_settings_handlers

load_dotenv()

async def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()

    # Add handlers
    for handler in get_handlers() + get_admin_handlers() + get_settings_handlers():
        application.add_handler(handler)

    print("Moon Bot is running...")
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=[])
        # Keep the bot running until stopped
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, lambda: stop_event.set())
        loop.add_signal_handler(signal.SIGTERM, lambda: stop_event.set())
        await stop_event.wait()
    finally:
        print("Shutting down Moon Bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        print("Event loop closed.")