import os
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
OUT = "downloads"
os.makedirs(OUT, exist_ok=True)

@app.on_message(filters.command(["gclone", "groupclone", "clonechat"], prefixes=PREFIXES))
@sudo_only
async def gclone_cmd(client, message: Message):
    args = message.command[1:]
    nums = [int(a) for a in args if a.lstrip("-").isdigit()]
    flags = {a.lower() for a in args if not a.lstrip("-").isdigit()}
    if len(nums) >= 2:
        source_id, target_id = nums[0], nums[1]
    elif len(nums) == 1:
        source_id, target_id = nums[0], message.chat.id
    else:
        return await message.reply_text("`·gclone -100src -100dst`\nflags: nophoto notitle nodesc")
    if source_id == target_id:
        return await message.reply_text("Source ≠ target")
    status = await message.reply_text("🔄 Cloning…")
    try:
        source = await client.get_chat(source_id)
        target = await client.get_chat(target_id)
    except Exception as e:
        return await status.edit_text(f"❌ `{e}`")
    done, errors = [], []
    if "notitle" not in flags and getattr(source, "title", None):
        try:
            await client.set_chat_title(target_id, source.title[:128])
            done.append(f"Title: **{source.title}**")
        except Exception as e:
            errors.append(f"Title: {e}")
    if "nodesc" not in flags:
        try:
            await client.set_chat_description(target_id, (getattr(source, "description", None) or "")[:255])
            done.append("Description OK")
        except Exception as e:
            errors.append(f"Desc: {e}")
    if "nophoto" not in flags and getattr(source, "photo", None):
        path = None
        try:
            path = await client.download_media(source.photo.big_file_id, file_name=OUT + "/")
            await client.set_chat_photo(target_id, photo=path)
            done.append("Photo OK")
        except Exception as e:
            errors.append(f"Photo: {e}")
        finally:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
    body = f"**{source.title}** → **{target.title}**\n"
    body += "\n".join(f"✅ {x}" for x in done)
    if errors:
        body += "\n" + "\n".join(f"⚠ {x}" for x in errors)
    await status.edit_text(body)
