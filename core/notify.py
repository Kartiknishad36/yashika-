"""Owner notifications → LOG_GROUP only (no Saved Messages)."""
from config import LOG_GROUP_ID


async def notify_owner(client, text: str, **kwargs):
    """Send to LOG_GROUP_ID. Skip if not configured."""
    if not LOG_GROUP_ID:
        print("[notify] LOG_GROUP_ID not set — skip")
        return None
    try:
        return await client.send_message(LOG_GROUP_ID, text, **kwargs)
    except Exception as e:
        print(f"[notify] fail: {e}")
        return None


async def notify_owner_photo(client, photo, caption: str = ""):
    if not LOG_GROUP_ID:
        return None
    try:
        return await client.send_photo(LOG_GROUP_ID, photo, caption=caption)
    except Exception as e:
        print(f"[notify] photo fail: {e}")
        return None
