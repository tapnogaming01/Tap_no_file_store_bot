from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import DEVELOPER_NAME, DEVELOPER_LINK, SUPPORT_GROUP

ABOUT_TEXT = f"""
🤖 **ABOUT THIS BOT**

• **Bot Name:** VJ Post Search Bot
• **Developer:** [{DEVELOPER_NAME}]({DEVELOPER_LINK})
• **Language:** Python 3.10+
• **Framework:** Pyrogram Async Engine
• **Database:** MongoDB Async Motor
• **Hosting:** Render Web Service (Docker)

💡 **यह कैसे काम करता है?**
यह Bot Master Source Channel को ऑटो-ट्रैक करता है। कैप्शन की पहली लाइन से Title एक्सट्रैक्ट करता है, Episode Counts पहचानता है और Dynamic Target Channels में Shortener Protected Deep Links शेयर करता है।
"""

@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client, message):
    await message.reply_text(
        text=ABOUT_TEXT,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back / Start", callback_data="start_btn")]])
    )

@Client.on_callback_query(filters.regex("about_btn"))
async def about_callback(client, query: CallbackQuery):
    await query.message.edit_text(
        text=ABOUT_TEXT,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP), InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_LINK)]])
    )
