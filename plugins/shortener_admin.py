from pyrogram import Client, filters
from config import ADMIN_ID
from database import update_shortener_config

@Client.on_message(filters.command("set_shortener") & filters.user(ADMIN_ID))
async def set_shortener_cmd(client, message):
    try:
        args = message.text.split(" ", 1)[1]
        domain, api_key = args.split("|")
        await update_shortener_config({"domain": domain.strip(), "api_key": api_key.strip()})
        await message.reply_text(f"✅ **Shortener API Updated!**\n🌐 **Domain:** `{domain.strip()}`\n🔑 **Key:** `{api_key.strip()}`")
    except Exception:
        await message.reply_text("❌ **Format:** `/set_shortener domain.com | api_key`")

@Client.on_message(filters.command("set_shortener_time") & filters.user(ADMIN_ID))
async def set_shortener_time_cmd(client, message):
    try:
        hours = float(message.command[1])
        await update_shortener_config({"validity_hours": hours})
        await message.reply_text(f"⏳ **Validity Time Updated!**\nअब टोकन **{hours} घंटे** तक वैलिड रहेगा।")
    except Exception:
        await message.reply_text("❌ **Format:** `/set_shortener_time 24` (Hours in number)")

@Client.on_message(filters.command("shortener_on") & filters.user(ADMIN_ID))
async def shortener_on_cmd(client, message):
    await update_shortener_config({"is_active": True})
    await message.reply_text("✅ **Shortener Mode ACTIVATED!**")

@Client.on_message(filters.command("shortener_off") & filters.user(ADMIN_ID))
async def shortener_off_cmd(client, message):
    await update_shortener_config({"is_active": False})
    await message.reply_text("🚫 **Shortener Mode DISABLED!**")
