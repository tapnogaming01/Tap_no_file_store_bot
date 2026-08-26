import asyncio
import logging
from aiohttp import web
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, PORT, LOG_CHANNEL

logging.basicConfig(level=logging.INFO)

app = Client(
    "vj_file_store_engine",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def handle_ping(request):
    return web.Response(text="VJ Engine 200 OK Active")

async def start_server():
    server = web.Server(handle_ping)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_server()
    await app.start()
    
    bot_info = await app.get_me()
    print(f"✅ BOT STARTED SUCCESSFULLY AS: @{bot_info.username}")
    
    # Direct Log Channel Notification Test
    try:
        await app.send_message(
            chat_id=LOG_CHANNEL, 
            text=f"⚡ **VJ File Store System Powered ON!**\n🤖 **Bot:** @{bot_info.username}\n🆔 **Log Channel ID Verified:** `{LOG_CHANNEL}`"
        )
        print("✅ LOG_CHANNEL notification sent successfully!")
    except Exception as e:
        print(f"❌ LOG_CHANNEL ERROR: Could not send message to LOG_CHANNEL ({LOG_CHANNEL}). Error: {e}")
        print("💡 FIX: Ensure Bot is added as ADMIN with Post Messages permission in your Log Channel and ID starts with -100")

    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
