import logging
from pyrogram import Client, filters
from database import get_target_channel, save_file_ref
from utils import parse_caption, get_channel_post_buttons
from config import SOURCE_CHANNEL, LOG_CHANNEL

# Dynamic Channel Handler (Handles both Channel Posts and Group Messages)
@Client.on_message(filters.chat(SOURCE_CHANNEL) | filters.channel)
@Client.on_edited_message(filters.chat(SOURCE_CHANNEL) | filters.channel)
async def auto_source_pipeline(client, message):
    # Strictly check if message is from your exact SOURCE_CHANNEL
    if message.chat.id != SOURCE_CHANNEL:
        return

    caption = message.caption or message.text or ""
    print(f"📩 New Post Detected in Source Channel ({SOURCE_CHANNEL}): {caption[:30]}...")

    # Log Raw Receipt to LOG_CHANNEL
    try:
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"📥 **Source Post Detected!**\n🆔 Msg ID: `{message.id}`\n📝 Caption: `{caption}`"
        )
    except Exception as e:
        print(f"❌ Failed to post to Log Channel: {e}")

    story_name, start_ep, end_ep = parse_caption(caption)

    if not story_name:
        try:
            await client.send_message(LOG_CHANNEL, "⚠️ **Skipped:** Caption ki 1st line se title extract nahi ho saka.")
        except Exception:
            pass
        return

    target_channel = await get_target_channel(story_name)
    if not target_channel:
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"⚠️ **Unmapped Story Skipped:** `{story_name}`\n\n"
                f"💡 Map karne ke liye Command chalayein:\n`/add_story {story_name} | TARGET_CHANNEL_ID`"
            )
        except Exception:
            pass
        return

    file_token = f"file_{message.id}"
    await save_file_ref(file_token, message.id, SOURCE_CHANNEL)

    ep_label = f"EPS {start_ep} - {end_ep}" if start_ep and end_ep and start_ep != end_ep else f"EPS {start_ep}" if start_ep else ""
    post_text = f"✨ **{story_name}** ✨\n**{ep_label}**\n───────────────────\n⚡ *Powered by File Store Engine*"
    markup = get_channel_post_buttons(start_ep, end_ep, file_token)

    try:
        await client.send_message(chat_id=target_channel, text=post_text, reply_markup=markup)
        await client.send_message(LOG_CHANNEL, f"🚀 **Successfully Posted to Target!**\n📖 Story: `{story_name}`\n📢 Target: `{target_channel}`")
    except Exception as e:
        print(f"❌ Failed to send to Target Channel ({target_channel}): {e}")
        try:
            await client.send_message(LOG_CHANNEL, f"❌ **Target Send Error:** `{e}`")
        except Exception:
            pass
