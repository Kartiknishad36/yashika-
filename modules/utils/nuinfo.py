"""
.nuinfo / .numinfo / .number — expanded phone intel

Legal: carrier, region, formats, timezone only.
No Aadhaar / KYC / home address (not available legally).
"""
import re
import os
from datetime import datetime, timezone

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
    from phonenumbers.phonenumberutil import number_type, PhoneNumberType, region_code_for_number
except ImportError:
    phonenumbers = None

# Common country calling codes
CC_HINT = {
    1: "US/Canada",
    7: "Russia/Kazakhstan",
    44: "United Kingdom",
    91: "India",
    92: "Pakistan",
    880: "Bangladesh",
    971: "UAE",
    966: "Saudi Arabia",
    61: "Australia",
    49: "Germany",
    33: "France",
    81: "Japan",
    86: "China",
    62: "Indonesia",
    63: "Philippines",
    60: "Malaysia",
    65: "Singapore",
    94: "Sri Lanka",
    977: "Nepal",
}


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
            "╔══ 📞 <b>NUINFO PREMIUM</b> ══╗\n\n"
            "Usage:\n"
            "• <code>.nuinfo +919876543210</code>\n"
            "• Reply to number/contact + <code>.nuinfo</code>\n\n"
            "Gets: valid · region · carrier · timezone · formats\n"
            "Optional: <code>NUMLOOKUP_API_KEY</code> env\n\n"
            "❌ Aadhaar / address / KYC — not available\n"
            "╚════════════════════════╝"
        )
        return

    lines = [
        "╔══ 📞 <b>NUMBER FULL INFO</b> ══╗",
        f"Input raw: <code>{num}</code>",
        f"⏱ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
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
            rfc = phonenumbers.format_number(
                pn, phonenumbers.PhoneNumberFormat.RFC3966
            )
            region = geocoder.description_for_number(pn, "en") or "—"
            region_hi = geocoder.description_for_number(pn, "hi") or ""
            region_local = geocoder.description_for_number(pn, "en") or "—"
            car = carrier.name_for_number(pn, "en") or "—"
            car_hi = carrier.name_for_number(pn, "hi") or ""
            tzs = list(pn_tz.time_zones_for_number(pn) or [])
            ntype = _line_type_name(pn)
            try:
                rcode = region_code_for_number(pn) or "—"
            except Exception:
                rcode = "—"
            cc = pn.country_code
            cc_hint = CC_HINT.get(cc, "—")

            lines += [
                "<b>── Validation ──</b>",
                f"Valid number: <b>{'✅ Yes' if valid else '❌ No'}</b>",
                f"Possible number: <b>{'Yes' if possible else 'No'}</b>",
                "",
                "<b>── Formats ──</b>",
                f"E.164: <code>{e164}</code>",
                f"International: <code>{intl}</code>",
                f"National: <code>{national}</code>",
                f"RFC3966: <code>{rfc}</code>",
                "",
                "<b>── Geography ──</b>",
                f"Country code: <code>+{cc}</code> ({cc_hint})",
                f"Region code: <code>{rcode}</code>",
                f"Region (EN): <b>{region}</b>",
            ]
            if region_hi and region_hi != region:
                lines.append(f"Region (HI): <b>{region_hi}</b>")
            lines += [
                f"National number: <code>{pn.national_number}</code>",
                f"Timezone(s): <code>{', '.join(tzs) if tzs else '—'}</code>",
                "",
                "<b>── Network ──</b>",
                f"Carrier (EN): <b>{car}</b>",
            ]
            if car_hi and car_hi != car:
                lines.append(f"Carrier (HI): <b>{car_hi}</b>")
            lines.append(f"Line type: <code>{ntype}</code>")
        except Exception as e:
            lines.append(f"Parse error: <code>{type(e).__name__}: {e}</code>")
    else:
        lines.append("⚠️ <code>phonenumbers</code> package missing on server")

    key = (NUMLOOKUP_API_KEY or os.getenv("NUMLOOKUP_API_KEY") or "").strip()
    if key:
        lines.append("\n<b>── Live API (NUMLOOKUP) ──</b>")
        url = f"https://apilayer.net/api/validate?access_key={key}&number={e164}"
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
                        ("local_format", "Local format"),
                        ("international_format", "International"),
                        ("country_prefix", "Prefix"),
                        ("country_code", "Country code"),
                        ("country_name", "Country name"),
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
            "\nℹ️ Live API off — set env <code>NUMLOOKUP_API_KEY</code>"
        )

    lines += [
        "",
        "<b>── Legal limits ──</b>",
        "❌ Owner full name / Aadhaar / home address",
        "❌ Linked SIMs / KYC dump / bank data",
        "✅ Carrier · region · line type · formats · TZ",
        "╚════════════════════════════╝",
    ]

    await message.reply_text("\n".join(lines))
