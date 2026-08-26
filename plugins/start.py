from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_file_ref, is_user_token_valid, grant_user_pass, get_shortener_config
from utils import get_start_buttons, generate_short_link
from config import LOG_CHANNEL, BOT_USERNAME

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user = message.from_user

    if len(message.command) > 1:
        token = message.command[1]

        # Shortener Token Pass Granting
        if token.startswith("verify_"):
            hours = await grant_user_pass(user.id)
            await message.reply_text(
                f"🎉 **Shortener Verified Successfully!**\n\n"
                f"आपका एक्सेस टोकन अगले **{hours} घंटे** के लिए एक्टिवेट हो गया है।\n"
                f"अब आप बिना किसी Shortener के फाइलें एक्सेस कर सकते हैं।"
            )
            return

        # Direct File Fetch Logic
        file_data = await get_file_ref(token)
        if not file_data:
            await message.reply_text("⚠️ **यह फाइल डिलीट हो चुकी है या अमान्य लिंक है।**")
            return

        is_valid = await is_user_token_valid(user.id)

        if not is_valid:
            config = await get_shortener_config()
            hours = config.get("validity_hours", 24.0)

            verify_url = f"https://t.me/{BOT_USERNAME}?start=verify_{user.id}"
            short_url = await generate_short_link(verify_url)

            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔓 Complete Shortener to Access File", url=short_url)],
                [InlineKeyboardButton("❓ How to Open Link", url="https://t.me/your_tutorial_link")]
            ])

            await message.reply_text(
                f"🔒 **Access Required!**\n\n"
                f"फाइल एक्सेस करने के लिए शॉर्टनर को बायपास करें।\n"
                f"बायपास करने पर आपका टोकन **{hours} घंटे** तक वैलिड रहेगा।",
                reply_markup=btn
            )
            return

        # Deliver File if Token Valid
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
            await message.reply_text("❌ फाइल डिलीवर करने में कोई समस्या आई।")
        return

    # Normal /start UI
    welcome_text = (
        f"👋 **नमस्ते {user.first_name}!**\n\n"
        f"मैं **VJ Post Search & Advanced File Store Engine** हूँ।\n"
        f"स्टोरी पोस्ट और फाइल्स के लिए नीचे दिए गए ऑप्शंस का उपयोग करें।"
    )
    await message.reply_text(text=welcome_text, reply_markup=get_start_buttons(), disable_web_page_preview=True)
