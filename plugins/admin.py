from pyrogram import Client, filters
from database import save_mapping, update_shortener_config
from config import ADMIN_ID

@Client.on_message(filters.command("add_story") & filters.user(ADMIN_ID) & filters.private)
async def add_story_handler(client, message):
    # अगर सिर्फ /add_story भेजा है बिना आर्गुमेंट के
    if len(message.command) < 2 or "|" not in message.text:
        await message.reply_text("❌ **Format:** `/add_story Story Name | Channel_ID`")
        return

    try:
        # कमांड के बाद का टेक्स्ट निकालना
        raw_text = message.text.split(" ", 1)[1]
        story, channel_id = raw_text.split("|", 1)
        
        story_name = story.strip().upper()
        ch_id = int(channel_id.strip())

        # MongoDB में मैपिंग सेव करना
        await save_mapping(story_name, ch_id)

        reply_text = (
            f"✅ **Story System Learned!**\n\n"
            f"📖 **Story:** `{story_name}`\n"
            f"📢 **Target:** `{ch_id}`"
        )
        await message.reply_text(reply_text)

    except ValueError:
        await message.reply_text("❌ **Invalid Channel ID!** Channel ID संख्या (integer) होनी चाहिए, जैसे: `-1003961183518`")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")


