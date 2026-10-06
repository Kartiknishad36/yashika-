from config import MONGO_URI, MONGO_DB

_client = None
_db = None


async def get_db():
    global _client, _db
    if not MONGO_URI:
        return None
    if _db is not None:
        return _db
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        _db = _client[MONGO_DB]
        await _client.admin.command("ping")
        print(f"[mongo] connected db={MONGO_DB}")
        return _db
    except Exception as e:
        print(f"[mongo] fail: {e}")
        _client = None
        _db = None
        return None


async def mongo_save_session(uid: int, session: str, meta=None):
    db = await get_db()
    if db is None:
        return False
    doc = {"uid": uid, "session": session, **(meta or {})}
    await db.sessions.update_one({"uid": uid}, {"$set": doc}, upsert=True)
    return True
