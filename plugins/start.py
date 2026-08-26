from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_file_ref, is_user_token_valid, grant_user_pass, get_shortener_config
from utils import get_start_buttons, generate_short_link, safe_url
from config import LOG_CHANNEL, BOT_USERNAME, SUPPORT_GROUP

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user = message.from_user

    if len(message.command) > 1:
        token = message.command[1]

        if token.startswith("verify_"):
            hours = await grant_user_pass(user.id)
            await message.reply_text(
                f"🎉 **Shortener Verified Successfully!**\n\n"
                f"आपकी Access Key अगले **{hours} घंटे** के लिए एक्टिवेट हो गई है।\n"
                f"अब आप बिना Shortener के डायरेक्ट फाइलें डाउनलोड कर सकते हैं।"
            )
            return

        file_data = await get_file_ref(token)
        if not file_data:
            await message.reply_text("⚠️ **यह फाइल डिलीट हो चुकी है या लिंक अमान्य है।**")
            return

        is_valid = await is_user_token_valid(user.id)

        if not is_valid:
            config = await get_shortener_config()
            hours = config.get("validity_hours", 24.0)

            verify_url = f"https://t.me/{BOT_USERNAME}?start=verify_{user.id}"
            short_url = await generate_short_link(verify_url)

            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔓 Bypass Shortener to Unlock File", url=safe_url(short_url))],
                [InlineKeyboardButton("❓ How to Open Link", url=safe_url(SUPPORT_GROUP))]
            ])

            await message.reply_text(
                f"🔒 **Access Required!**\n\n"
                f"फाइल एक्सेस करने के लिए शॉर्टनर वेरिफिकेशन पूरा करें।\n"
                f"वेरिफिकेशन पूरा होने पर आपका टोकन **{hours} घंटे** तक वैलिड रहेगा।",
                reply_markup=btn
            )
            return

        try:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=file_data["chat_id"],
                message_id=file_data["msg_id"]
            )
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=f"📥 **File Delivered**\n👤 User: [{user.first_name}](tg://user?id={user.id})\n🆔 ID: `{user.id}`"
            )
        except Exception as e:
            await message.reply_text(f"❌ फाइल डिलीवर करने में विफलता: `{e}`")
        return

    welcome_text = (
        f"👋 **नमस्ते {user.first_name}!**\n\n"
        f"मैं **VJ Post Search & Advanced File Store Engine** हूँ।\n"
        f"स्टोरी फाइल्स प्राप्त करने के लिए चैनल लिंक्स पर क्लिक करें।"
    )
    await message.reply_text(text=welcome_text, reply_markup=get_start_buttons(), disable_web_page_preview=True)
