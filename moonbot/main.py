import os
import asyncio
from telegram.ext import Application
from dotenv import load_dotenv
from handlers import get_handlers

load_dotenv()

async def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()

    # Add handlers
    for handler in get_handlers():
        application.add_handler(handler)

    print("Moon Bot is running...")
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=[])
        # Keep the bot running until stopped
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If an event loop is already running, create a task
            loop.create_task(main())
            loop.run_forever()
        else:
            # If no event loop is running, run normally
            loop.run_until_complete(main())
    except RuntimeError as e:
        print(f"Event loop error: {e}")
    finally:
        loop.close()