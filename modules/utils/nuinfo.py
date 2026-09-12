"""
.nuinfo <number>  | reply to a msg containing number
Phone basic parse + optional API (NUMLOOKUP_API_KEY).
"""
import re
import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from config import OWNER_ID

PREFIXES = [".", "!"]

try:
    from config import NUMLOOKUP_API_KEY
except ImportError:
    NUMLOOKUP_API_KEY = ""

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
except ImportError:
    phonenumbers = None


def _extract_number(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(\+?\d[\d\-\s()]{7,}\d)", text)
    return re.sub(r"[^\d+]", "", m.group(1)) if m else ""


@app.on_message(filters.command(["nuinfo", "numinfo", "number"], prefixes=PREFIXES))
@sudo_only
async def nuinfo_cmd(client, message: Message):
    raw = ""
    if len(message.command) > 1:
        raw = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        raw = message.reply_to_message.text or message.reply_to_message.caption or ""
    num = _extract_number(raw)
    if not num:
        await message.reply_text(
            "Usage:\n`.nuinfo +919876543210`\nReply to number + `.nuinfo`"
        )
        return

    lines = [f"📞 <b>Number Info</b>\n<code>{num}</code>\n"]

    if phonenumbers:
        try:
            if not num.startswith("+"):
                # default India if 10 digit
                pn = phonenumbers.parse(num, "IN")
            else:
                pn = phonenumbers.parse(num, None)
            valid = phonenumbers.is_valid_number(pn)
            lines.append(f"Valid: <b>{'Yes' if valid else 'No'}</b>")
            lines.append(
                f"International: <code>{phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}</code>"
            )
            lines.append(
                f"E164: <code>{phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)}</code>"
            )
            region = geocoder.description_for_number(pn, "en") or "—"
            lines.append(f"Region: <b>{region}</b>")
            car = carrier.name_for_number(pn, "en") or "—"
            lines.append(f"Carrier: <b>{car}</b>")
            tzs = timezone.time_zones_for_number(pn) or []
            lines.append(f"Timezone: <code>{', '.join(tzs) if tzs else '—'}</code>")
            lines.append(f"Country code: <code>+{pn.country_code}</code>")
        except Exception as e:
            lines.append(f"Parse error: `{e}`")
    else:
        lines.append("ℹ️ Install <code>phonenumbers</code> for local parse.")

    # Optional live API
    key = (NUMLOOKUP_API_KEY or "").strip()
    if key:
        e164 = num if num.startswith("+") else f"+{num}"
        url = f"https://apilayer.net/api/validate?access_key={key}&number={e164}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()
            if isinstance(data, dict):
                lines.append("\n🌐 <b>API</b>")
                for k in (
                    "valid", "number", "local_format", "international_format",
                    "country_name", "location", "carrier", "line_type",
                ):
                    if k in data and data[k] not in (None, ""):
                        lines.append(f"{k}: <code>{data[k]}</code>")
        except Exception as e:
            lines.append(f"API error: `{e}`")

    await message.reply_text("\n".join(lines))
