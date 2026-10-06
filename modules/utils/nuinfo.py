"""
.nuinfo / .numinfo / .number

  .nuinfo +919876543210
  reply to msg with number + .nuinfo

Local: phonenumbers (valid, region, carrier, timezone, formats)
Optional: NUMLOOKUP_API_KEY in env → apilayer validate

NOTE (legal):
  Aadhaar, owner name, home address, linked SIMs — Telegram/public API
  se nahi milte. Government/telecom KYC data unauthorized access illegal.
"""
import re
import os

import aiohttp
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

try:
    from config import NUMLOOKUP_API_KEY
except ImportError:
    NUMLOOKUP_API_KEY = os.getenv("NUMLOOKUP_API_KEY", "")

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as pn_tz
    from phonenumbers.phonenumberutil import number_type, PhoneNumberType
except ImportError:
    phonenumbers = None


def _extract_number(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(\+?\d[\d\-\s()]{7,}\d)", text)
    return re.sub(r"[^\d+]", "", m.group(1)) if m else ""


def _line_type_name(pn) -> str:
    if not phonenumbers:
        return "—"
    try:
        t = number_type(pn)
        mapping = {
            PhoneNumberType.MOBILE: "Mobile",
            PhoneNumberType.FIXED_LINE: "Fixed line",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed/Mobile",
            PhoneNumberType.TOLL_FREE: "Toll free",
            PhoneNumberType.PREMIUM_RATE: "Premium rate",
            PhoneNumberType.VOIP: "VoIP",
            PhoneNumberType.PAGER: "Pager",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.VOICEMAIL: "Voicemail",
            PhoneNumberType.SHARED_COST: "Shared cost",
        }
        return mapping.get(t, str(t))
    except Exception:
        return "—"


@app.on_message(ub_cmd("nuinfo", "numinfo", "number"))
@sudo_only
async def nuinfo_cmd(client, message: Message):
    raw = ""
    parts = (message.text or "").split(None, 1)
    if len(parts) > 1:
        raw = parts[1]
    elif message.reply_to_message:
        r = message.reply_to_message
        raw = r.text or r.caption or ""
        if not raw and r.contact:
            raw = r.contact.phone_number or ""

    num = _extract_number(raw)
    if not num:
        await message.reply_text(
            "╔══ 📞 <b>NUINFO</b> ══╗\n"
            "Usage:\n"
            "<code>.nuinfo +919876543210</code>\n"
            "Reply to number + <code>.nuinfo</code>\n\n"
            "<i>Optional env: NUMLOOKUP_API_KEY</i>\n"
            "╚══════════════╝"
        )
        return

    lines = [
        "╔══ 📞 <b>NUMBER INFO</b> ══╗",
        f"Input: <code>{num}</code>",
        "",
    ]

    e164 = num
    if phonenumbers:
        try:
            if not num.startswith("+"):
                pn = phonenumbers.parse(num, "IN")
            else:
                pn = phonenumbers.parse(num, None)

            valid = phonenumbers.is_valid_number(pn)
            possible = phonenumbers.is_possible_number(pn)
            e164 = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
            intl = phonenumbers.format_number(
                pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            national = phonenumbers.format_number(
                pn, phonenumbers.PhoneNumberFormat.NATIONAL
            )
            region = geocoder.description_for_number(pn, "en") or "—"
            region_hi = geocoder.description_for_number(pn, "hi") or ""
            car = carrier.name_for_number(pn, "en") or "—"
            tzs = list(pn_tz.time_zones_for_number(pn) or [])
            ntype = _line_type_name(pn)

            lines += [
                "<b>── Local parse ──</b>",
                f"Valid: <b>{'✅ Yes' if valid else '❌ No'}</b>",
                f"Possible: <b>{'Yes' if possible else 'No'}</b>",
                f"E164: <code>{e164}</code>",
                f"International: <code>{intl}</code>",
                f"National: <code>{national}</code>",
                f"Country code: <code>+{pn.country_code}</code>",
                f"National number: <code>{pn.national_number}</code>",
                f"Region: <b>{region}</b>"
                + (f" ({region_hi})" if region_hi and region_hi != region else ""),
                f"Carrier: <b>{car}</b>",
                f"Line type: <code>{ntype}</code>",
                f"Timezone: <code>{', '.join(tzs) if tzs else '—'}</code>",
            ]
        except Exception as e:
            lines.append(f"Parse error: <code>{e}</code>")
    else:
        lines.append("⚠️ <code>phonenumbers</code> package missing on server")

    # Optional live API
    key = (NUMLOOKUP_API_KEY or os.getenv("NUMLOOKUP_API_KEY") or "").strip()
    if key:
        lines.append("\n<b>── Live API ──</b>")
        url = (
            f"https://apilayer.net/api/validate"
            f"?access_key={key}&number={e164}"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    data = await resp.json()
            if isinstance(data, dict):
                if data.get("error"):
                    lines.append(f"API error: <code>{data.get('error')}</code>")
                else:
                    for k, label in [
                        ("valid", "Valid"),
                        ("number", "Number"),
                        ("local_format", "Local"),
                        ("international_format", "International"),
                        ("country_prefix", "Prefix"),
                        ("country_code", "Country code"),
                        ("country_name", "Country"),
                        ("location", "Location"),
                        ("carrier", "Carrier"),
                        ("line_type", "Line type"),
                    ]:
                        if k in data and data[k] not in (None, ""):
                            lines.append(f"{label}: <code>{data[k]}</code>")
            else:
                lines.append("API: unexpected response")
        except Exception as e:
            lines.append(f"API error: <code>{e}</code>")
    else:
        lines.append(
            "\nℹ️ Live API off — env me <code>NUMLOOKUP_API_KEY</code> set karo"
        )

    lines += [
        "",
        "<b>── Limits ──</b>",
        "❌ Owner name / Aadhaar / home address",
        "❌ Linked other numbers / KYC dump",
        "✅ Carrier · region · line type · formats",
        "╚════════════════╝",
    ]

    await message.reply_text("\n".join(lines))
