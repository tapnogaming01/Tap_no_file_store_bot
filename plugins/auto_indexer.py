from pyrogram import Client, filters
from database import get_target_channel, save_file_ref
from utils import parse_caption, get_channel_post_buttons
from config import SOURCE_CHANNEL, LOG_CHANNEL

# Dynamic Filter for Source Channel (Guarantees Event Delivery)
def is_source_channel(_, __, message):
    return message.chat and message.chat.id == SOURCE_CHANNEL

@Client.on_message(filters.create(is_source_channel), group=-1)
@Client.on_edited_message(filters.create(is_source_channel), group=-1)
async def auto_source_pipeline(client, message):
    try:
        caption = message.caption or message.text or ""
        
        # Verbose Log to ensure Message Detection
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"📥 **Source Channel Catch Triggered!**\n\n🆔 Msg ID: `{message.id}`\n📝 Caption: `{caption}`"
        )

        story_name, start_ep, end_ep = parse_caption(caption)

        if not story_name:
            await client.send_message(LOG_CHANNEL, "⚠️ **Skipped:** Caption ki 1st line se title extract nahi ho saka.")
            return

        target_channel = await get_target_channel(story_name)
        if not target_channel:
            await client.send_message(
                LOG_CHANNEL,
                f"⚠️ **Unmapped Story Skipped:** `{story_name}`\n\n"
                f"💡 Map karne ke liye Command chalayein:\n`/add_story {story_name} | TARGET_CHANNEL_ID`"
            )
            return

        file_token = f"file_{message.id}"
        await save_file_ref(file_token, message.id, SOURCE_CHANNEL)

        ep_label = f"EPS {start_ep} - {end_ep}" if start_ep and end_ep and start_ep != end_ep else f"EPS {start_ep}" if start_ep else ""
        post_text = f"✨ **{story_name}** ✨\n**{ep_label}**\n───────────────────\n⚡ *Powered by File Store Engine*"
        markup = get_channel_post_buttons(start_ep, end_ep, file_token)

        await client.send_message(chat_id=target_channel, text=post_text, reply_markup=markup)
        await client.send_message(LOG_CHANNEL, f"🚀 **Successfully Posted to Target!**\n📖 Story: `{story_name}`\n📢 Target: `{target_channel}`")

    except Exception as e:
        await client.send_message(LOG_CHANNEL, f"❌ **Pipeline Exception Error:** `{e}`")
