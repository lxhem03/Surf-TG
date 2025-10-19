import asyncio
from traceback import format_exc
from aiohttp import web

from bot import __version__, LOGGER
from bot.config import Telegram
from bot.server import web_server
from bot.telegram import StreamBot, UserBot
from bot.telegram.clients import initialize_clients


async def start_services():
    LOGGER.info(f"Initializing Surf-TG v-{__version__}")
    await asyncio.sleep(1.2)

    # Start main bot
    await StreamBot.start()
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"Bot Client : [@{StreamBot.username}]")

    # Start userbot if session exists
    if Telegram.SESSION_STRING:
        await UserBot.start()
        UserBot.username = (
            UserBot.me.username or UserBot.me.first_name or UserBot.me.id
        )
        LOGGER.info(f"User Client : {UserBot.username}")

    # Initialize additional clients
    LOGGER.info("Initializing Multi Clients")
    await initialize_clients()

    # Setup web server
    LOGGER.info("Initializing Surf Web Server..")
    runner = web.AppRunner(await web_server())
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", Telegram.PORT).start()
    LOGGER.info(f"Web server running on port {Telegram.PORT}")

    # Keep running forever (replaces idle())
    LOGGER.info("Surf-TG Started Revolving!")
    await asyncio.Event().wait()


async def stop_clients():
    try:
        await StreamBot.stop()
    except Exception:
        pass
    if Telegram.SESSION_STRING:
        try:
            await UserBot.stop()
        except Exception:
            pass


def main():
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        LOGGER.info("Service Stopping...")
    except Exception:
        LOGGER.error(format_exc())
    finally:
        try:
            asyncio.run(stop_clients())
        except Exception:
            pass


if __name__ == "__main__":
    main()
