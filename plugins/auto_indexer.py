# plugins/auto_indexer.py
from pyrogram import Client, filters
from database import get_target_channel, save_file_ref
from utils import parse_caption, get_channel_post_buttons
from config import SOURCE_CHANNEL, LOG_CHANNEL

@Client.on_message(filters.chat(SOURCE_CHANNEL) & (filters.document | filters.audio | filters.video))
async def auto_source_pipeline(client, message):
    caption = message.caption or message.text or ""
    
    # Debug Logging: यह चेक करने के लिए कि पोस्ट बोट तक पहुँच रही है या नहीं
    await client.send_message(LOG_CHANNEL, f"📩 **New Media Received in Source Channel!**\nRaw Caption: `{caption}`")

    story_name, start_ep, end_ep = parse_caption(caption)

    if not story_name:
        await client.send_message(LOG_CHANNEL, "⚠️ **Parsing Failed:** Caption की पहली लाइन से Title नहीं मिला।")
        return

    target_channel = await get_target_channel(story_name)
    if not target_channel:
        await client.send_message(
            LOG_CHANNEL, 
            f"⚠️ **Unmapped Story:** `{story_name}` डेटाबेस में नहीं मिली।\n"
            f"इसे जोड़ने के लिए चलाएँ: `/add_story {story_name} | TARGET_CHANNEL_ID`"
        )
        return

    file_token = f"file_{message.id}"
    await save_file_ref(file_token, message.id, SOURCE_CHANNEL)

    ep_label = f"EPS {start_ep} - {end_ep}" if start_ep and end_ep and start_ep != end_ep else f"EPS {start_ep}" if start_ep else ""
    post_text = f"✨ **{story_name}** ✨\n**{ep_label}**\n───────────────────\n⚡ *Powered by File Store Engine*"
    markup = get_channel_post_buttons(start_ep, end_ep, file_token)

    try:
        await client.send_message(chat_id=target_channel, text=post_text, reply_markup=markup)
        await client.send_message(LOG_CHANNEL, f"🚀 **Successfully Posted to Target!**\nStory: `{story_name}`")
    except Exception as e:
        await client.send_message(LOG_CHANNEL, f"❌ **Target Send Error:** `{e}`")
