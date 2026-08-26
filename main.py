import asyncio
from aiohttp import web
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, PORT, LOG_CHANNEL

app = Client(
    "vj_file_store_engine",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def handle_ping(request):
    return web.Response(text="VJ File Store Engine: 200 OK Active")

async def start_server():
    server = web.Server(handle_ping)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_server()
    await app.start()
    try:
        await app.send_message(LOG_CHANNEL, "⚡ **VJ File Store System Powered ON!**")
    except Exception as e:
        print(f"Log Notice Error: {e}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
