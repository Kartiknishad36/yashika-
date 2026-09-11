"""
Sticker Kang (userbot):
  Reply to sticker / photo → .kang [emoji]
  Pack: a_{user_id}_by_{bot_username}  OR user pack via create_sticker_set

Pyrogram user account: create_sticker_set needs stickers.telegram.org style;
works best when linked bot username exists (BOT_USERNAME).
"""
import io
import os
import random
import tempfile

from pyrogram import filters, raw
from pyrogram.types import Message
from pyrogram.errors import StickersetInvalid, PeerIdInvalid

from core.clients import app
from config import BOT_USERNAME, BOT_NAME
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def _pack_name(user_id: int) -> str:
    # Telegram: pack short_name must be unique, a-z0-9 _
    base = (BOT_USERNAME or "yashika").lower().replace("@", "")
    return f"u{user_id}_by_{base}"


def _pack_title(user_id: int) -> str:
    return f"{BOT_NAME or 'Yashika'} Kang Pack"


@app.on_message(filters.command(["kang", "steal"], prefixes=PREFIXES))
@sudo_only
async def kang_cmd(client, message: Message):
    reply = message.reply_to_message
    if not reply:
        await message.reply_text("Reply to a **sticker** or **photo** with `.kang` [emoji]")
        return

    emoji = "🙂"
    if len(message.command) > 1:
        emoji = message.command[1][:3]

    status = await message.reply_text("🔪 Kanging...")

    me = await client.get_me()
    short_name = _pack_name(me.id)
    title = _pack_title(me.id)

    # --- get sticker file (webp/tgs/webm) or photo ---
    tmp_path = None
    is_animated = False
    is_video = False

    try:
        if reply.sticker:
            is_animated = bool(reply.sticker.is_animated)
            is_video = bool(reply.sticker.is_video)
            if not reply.sticker.emoji and len(message.command) < 2:
                emoji = reply.sticker.emoji or emoji
            elif reply.sticker.emoji and len(message.command) < 2:
                emoji = reply.sticker.emoji
            tmp_path = await client.download_media(reply.sticker)
        elif reply.photo:
            tmp_path = await client.download_media(reply.photo)
            # resize-ish: Telegram accepts photo; convert via stickers often needs webp
            # send as document sticker input — try upload as photo sticker
        elif reply.document and (reply.document.mime_type or "").startswith("image/"):
            tmp_path = await client.download_media(reply.document)
        else:
            await status.edit_text("Sirf sticker / photo pe `.kang` karo.")
            return

        if not tmp_path or not os.path.exists(tmp_path):
            await status.edit_text("❌ Download fail.")
            return

        # Upload file to Telegram
        with open(tmp_path, "rb") as f:
            uploaded = await client.save_file(f)

        # Build InputDocument for sticker
        media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer("me"),
                media=raw.types.InputMediaUploadedDocument(
                    file=uploaded,
                    mime_type="application/x-tgsticker"
                    if is_animated
                    else ("video/webm" if is_video else "image/webp"),
                    attributes=[
                        raw.types.DocumentAttributeFilename(
                            file_name=os.path.basename(tmp_path)
                        )
                    ],
                ),
            )
        )

        doc = media.document
        input_doc = raw.types.InputDocument(
            id=doc.id,
            access_hash=doc.access_hash,
            file_reference=doc.file_reference,
        )

        sticker_item = raw.types.InputStickerSetItem(
            document=input_doc,
            emoji=emoji,
        )

        # Try add to existing pack, else create
        try:
            await client.invoke(
                raw.functions.stickers.AddStickerToSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=short_name),
                    sticker=sticker_item,
                )
            )
        except StickersetInvalid:
            await client.invoke(
                raw.functions.stickers.CreateStickerSet(
                    user_id=raw.types.InputUserSelf(),
                    title=title,
                    short_name=short_name,
                    stickers=[sticker_item],
                    animated=is_animated,
                    videos=is_video,
                )
            )
        except Exception as e:
            # create if add failed for other reasons
            try:
                await client.invoke(
                    raw.functions.stickers.CreateStickerSet(
                        user_id=raw.types.InputUserSelf(),
                        title=title,
                        short_name=short_name,
                        stickers=[sticker_item],
                        animated=is_animated,
                        videos=is_video,
                    )
                )
            except Exception as e2:
                await status.edit_text(f"❌ Kang fail:\n`{e}`\n`{e2}`")
                return

        link = f"https://t.me/addstickers/{short_name}"
        await status.edit_text(
            f"✅ Kanged {emoji}\nPack: <a href=\"{link}\">{title}</a>"
        )
    except Exception as e:
        await status.edit_text(f"❌ Error: `{e}`")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
