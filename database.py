import time
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client["Tap_no_file"]

shortener_settings = db["shortener_settings"]
user_pass_tokens = db["user_pass_tokens"]
files = db["stored_files"]
mappings = db["story_mappings"]

async def get_shortener_config():
    config = await shortener_settings.find_one({"type": "config"})
    if not config:
        default_config = {
            "type": "config",
            "is_active": True,
            "domain": "gplinks.in",
            "api_key": "YOUR_SHORTENER_API_KEY",
            "validity_hours": 24.0
        }
        await shortener_settings.insert_one(default_config)
        return default_config
    return config

async def update_shortener_config(data: dict):
    await shortener_settings.update_one({"type": "config"}, {"$set": data}, upsert=True)

async def is_user_token_valid(user_id: int):
    config = await get_shortener_config()
    if not config.get("is_active", True):
        return True

    user_data = await user_pass_tokens.find_one({"user_id": user_id})
    if not user_data:
        return False

    expiry_time = user_data.get("expiry_timestamp", 0)
    return time.time() < expiry_time

async def grant_user_pass(user_id: int):
    config = await get_shortener_config()
    hours = config.get("validity_hours", 24.0)
    expiry_timestamp = time.time() + (hours * 3600)

    await user_pass_tokens.update_one(
        {"user_id": user_id},
        {"$set": {"expiry_timestamp": expiry_timestamp, "granted_at": time.time()}},
        upsert=True
    )
    return hours

async def save_file_ref(file_token: str, msg_id: int, chat_id: int):
    await files.update_one(
        {"token": file_token},
        {"$set": {"msg_id": msg_id, "chat_id": chat_id}},
        upsert=True
    )

async def get_file_ref(file_token: str):
    return await files.find_one({"token": file_token})

async def save_mapping(story_name: str, channel_id: int):
    await mappings.update_one(
        {"story": story_name.strip().upper()},
        {"$set": {"channel_id": channel_id}},
        upsert=True
    )

async def get_target_channel(story_name: str):
    doc = await mappings.find_one({"story": story_name.strip().upper()})
    return doc["channel_id"] if doc else None
