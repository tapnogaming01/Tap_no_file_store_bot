import re
import aiohttp
import urllib.parse
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME, DEVELOPER_LINK, SUPPORT_GROUP, MAIN_CHANNEL
from database import get_shortener_config

def parse_caption(caption: str):
    if not caption:
        return None, None, None

    # Remove multi-lines, extract 1st line strictly
    lines = [line.strip() for line in caption.split("\n") if line.strip()]
    if not lines:
        return None, None, None
        
    first_line = lines[0]

    # Pattern Match: EPS 01-10 or EPISODE 1 TO 10
    range_match = re.search(r'(?:EPS|EP|EPISODE|EPISODES)?\s*(\d+)\s*(?:-|TO|\b)\s*(\d+)', first_line, re.IGNORECASE)
    if range_match:
        start_ep = int(range_match.group(1))
        end_ep = int(range_match.group(2))
        story_name = first_line[:range_match.start()].strip().rstrip("-|:").strip()
        return story_name.upper() if story_name else "STORY BATCH", start_ep, end_ep

    # Pattern Match: Single EP 01
    single_match = re.search(r'(?:EPS|EP|EPISODE)?\s*(\d+)', first_line, re.IGNORECASE)
    if single_match:
        ep_num = int(single_match.group(1))
        story_name = first_line[:single_match.start()].strip().rstrip("-|:").strip()
        return story_name.upper() if story_name else "STORY BATCH", ep_num, ep_num

    return first_line.upper(), None, None

async def generate_short_link(long_url: str):
    config = await get_shortener_config()
    domain = config.get("domain")
    api_key = config.get("api_key")

    api_url = f"https://{domain}/api?api={api_key}&url={urllib.parse.quote(long_url)}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                data = await response.json()
                if data.get("status") == "success" or "shortlink" in data:
                    return data.get("shortlink")
    except Exception as e:
        print(f"Shortener Engine Error: {e}")
    
    return long_url

def get_channel_post_buttons(start_ep, end_ep, file_token):
    if start_ep and end_ep:
        label = f"EPS {start_ep} - {end_ep}" if start_ep != end_ep else f"EPISODE {start_ep}"
    elif start_ep:
        label = f"EPISODE {start_ep}"
    else:
        label = "GET FILE ACCESS"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📥 {label} ↗️", url=f"https://t.me/{BOT_USERNAME}?start={file_token}")],
        [InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_GROUP), InlineKeyboardButton("📢 CHANNEL", url=MAIN_CHANNEL)],
        [InlineKeyboardButton("👨‍💻 DEVELOPER", url=DEVELOPER_LINK)]
    ])

def get_start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Main Channel", url=MAIN_CHANNEL), InlineKeyboardButton("💬 Support Group", url=SUPPORT_GROUP)],
        [InlineKeyboardButton("ℹ️ About Bot", callback_data="about_btn"), InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_LINK)]
    ])
