import asyncio
from traceback import format_exc
from aiohttp import web

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ------------------------------------------------

from pyrogram import idle

from bot import __version__, LOGGER
from bot.config import Telegram
from bot.server import web_server
from bot.telegram import StreamBot, UserBot
from bot.telegram.clients import initialize_clients


async def start_services():
    LOGGER.info(f"Initializing Surf-TG v-{__version__}")
    await asyncio.sleep(1.2)

    # Start main bot client
    await StreamBot.start()
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"Bot Client : [@{StreamBot.username}]")

    # Start userbot client if available
    if len(Telegram.SESSION_STRING) != 0:
        await UserBot.start()
        UserBot.username = UserBot.me.username or UserBot.me.first_name or UserBot.me.id
        LOGGER.info(f"User Client : {UserBot.username}")

    await asyncio.sleep(1.2)
    LOGGER.info("Initializing Multi Clients")
    await initialize_clients()

    await asyncio.sleep(2)
    LOGGER.info("Initializing Surf Web Server..")
    server = web.AppRunner(await web_server())

    LOGGER.info("Server CleanUp!")
    await server.cleanup()

    await asyncio.sleep(2)
    LOGGER.info("Server Setup Started !")

    await server.setup()
    await web.TCPSite(server, "0.0.0.0", Telegram.PORT).start()

    LOGGER.info("Surf-TG Started Revolving !")
    await idle()  # Keeps the bot running


async def stop_clients():
    await StreamBot.stop()
    if len(Telegram.SESSION_STRING) != 0:
        await UserBot.stop()


if __name__ == "__main__":
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
