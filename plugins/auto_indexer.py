from pyrogram import Client, filters
from database import get_target_channel, save_file_ref
from utils import parse_caption, get_channel_post_buttons
from config import SOURCE_CHANNEL, LOG_CHANNEL

@Client.on_message(filters.chat(SOURCE_CHANNEL) & (filters.document | filters.audio | filters.video))
async def auto_source_pipeline(client, message):
    caption = message.caption or message.text or ""
    story_name, start_ep, end_ep = parse_caption(caption)

    if not story_name:
        return

    target_channel = await get_target_channel(story_name)
    if not target_channel:
        await client.send_message(LOG_CHANNEL, f"⚠️ **Unmapped Post Ignored**\nDetected Title: `{story_name}`")
        return

    file_token = f"file_{message.id}"
    await save_file_ref(file_token, message.id, SOURCE_CHANNEL)

    ep_label = f"EPS {start_ep} - {end_ep}" if start_ep and end_ep and start_ep != end_ep else f"EPS {start_ep}" if start_ep else ""
    post_text = f"✨ **{story_name}** ✨\n**{ep_label}**\n───────────────────\n⚡ *Powered by VJ File Store Engine*"
    markup = get_channel_post_buttons(start_ep, end_ep, file_token)

    await client.send_message(chat_id=target_channel, text=post_text, reply_markup=markup)
    await client.send_message(LOG_CHANNEL, f"🚀 **Auto Posted**\nStory: `{story_name}`\nTarget: `{target_channel}`")
