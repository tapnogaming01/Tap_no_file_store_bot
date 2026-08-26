from pyrogram import Client, filters
from database import save_mapping
from config import ADMIN_ID, LOG_CHANNEL

@Client.on_message(filters.command("add_story") & filters.user(ADMIN_ID))
async def add_story_cmd(client, message):
    try:
        args = message.text.split(" ", 1)[1]
        story, channel_id = args.split("|")
        story_clean = story.strip().upper()
        target_id = int(channel_id.strip())

        await save_mapping(story_clean, target_id)
        
        await message.reply_text(f"✅ **Story System Learned!**\n\n📖 **Story:** `{story_clean}`\n📢 **Target:** `{target_id}`")
        await client.send_message(LOG_CHANNEL, f"🛠 **New Target Mapping Added**\nStory: `{story_clean}` ➡️ Channel: `{target_id}`")
    except Exception:
        await message.reply_text("❌ **Format:** `/add_story Story Name | Channel_ID`")
