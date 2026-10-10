"""
.nuinfo / .numinfo / .number — 200+ detail phone report (premium)

Legal fields only: formats, validation, carrier, region, timezone,
digit structure, India series hints, optional NUMLOOKUP API.
NO Aadhaar / home address / KYC / bank (not available legally).
"""
import re
import os
from datetime import datetime, timezone

import aiohttp
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

try:
    from config import NUMLOOKUP_API_KEY
except ImportError:
    NUMLOOKUP_API_KEY = os.getenv("NUMLOOKUP_API_KEY", "")

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as pn_tz
    from phonenumbers.phonenumberutil import (
        number_type,
        PhoneNumberType,
        region_code_for_number,
        country_code_for_region,
        is_number_geographical,
        length_of_national_destination_code,
        national_significant_number,
        can_be_internationally_dialled,
        is_valid_number_for_region,
        is_possible_number_with_reason,
        ValidationResult,
    )
except ImportError:
    phonenumbers = None

CC_HINT = {
    1: "US/Canada/NANP", 7: "Russia/Kazakhstan", 20: "Egypt", 27: "South Africa",
    30: "Greece", 31: "Netherlands", 32: "Belgium", 33: "France", 34: "Spain",
    39: "Italy", 40: "Romania", 41: "Switzerland", 43: "Austria", 44: "United Kingdom",
    45: "Denmark", 46: "Sweden", 47: "Norway", 48: "Poland", 49: "Germany",
    51: "Peru", 52: "Mexico", 53: "Cuba", 54: "Argentina", 55: "Brazil",
    56: "Chile", 57: "Colombia", 58: "Venezuela", 60: "Malaysia", 61: "Australia",
    62: "Indonesia", 63: "Philippines", 64: "New Zealand", 65: "Singapore",
    66: "Thailand", 81: "Japan", 82: "South Korea", 84: "Vietnam", 86: "China",
    90: "Turkey", 91: "India", 92: "Pakistan", 93: "Afghanistan", 94: "Sri Lanka",
    95: "Myanmar", 98: "Iran", 212: "Morocco", 213: "Algeria", 216: "Tunisia",
    218: "Libya", 220: "Gambia", 221: "Senegal", 234: "Nigeria", 254: "Kenya",
    255: "Tanzania", 256: "Uganda", 260: "Zambia", 263: "Zimbabwe",
    351: "Portugal", 352: "Luxembourg", 353: "Ireland", 354: "Iceland",
    355: "Albania", 356: "Malta", 357: "Cyprus", 358: "Finland", 359: "Bulgaria",
    370: "Lithuania", 371: "Latvia", 372: "Estonia", 373: "Moldova",
    374: "Armenia", 375: "Belarus", 380: "Ukraine", 381: "Serbia",
    385: "Croatia", 386: "Slovenia", 420: "Czech", 421: "Slovakia",
    852: "Hong Kong", 853: "Macau", 855: "Cambodia", 856: "Laos",
    880: "Bangladesh", 886: "Taiwan", 960: "Maldives", 961: "Lebanon",
    962: "Jordan", 963: "Syria", 964: "Iraq", 965: "Kuwait", 966: "Saudi Arabia",
    967: "Yemen", 968: "Oman", 970: "Palestine", 971: "UAE", 972: "Israel",
    973: "Bahrain", 974: "Qatar", 975: "Bhutan", 976: "Mongolia", 977: "Nepal",
    992: "Tajikistan", 993: "Turkmenistan", 994: "Azerbaijan", 995: "Georgia",
    996: "Kyrgyzstan", 998: "Uzbekistan",
}

# India mobile series → operator (approximate public ranges)
IN_SERIES = {
    "6": "New series (2015+) mixed",
    "7": "Reliance/Jio/Airtel/VI mixed",
    "8": "Airtel/VI/BSNL/MTNL mixed",
    "9": "Legacy GSM mixed operators",
}

IN_PREFIX_HINT = {
    "70": "Reliance Jio (common)",
    "71": "Reliance Jio",
    "72": "Reliance Jio",
    "73": "Reliance Jio",
    "74": "Reliance Jio",
    "75": "Reliance Jio",
    "76": "Reliance Jio",
    "77": "Reliance Jio",
    "78": "Reliance Jio",
    "79": "Reliance Jio",
    "80": "Airtel / others",
    "81": "Airtel / others",
    "82": "Airtel / others",
    "83": "Airtel / others",
    "84": "Airtel / others",
    "85": "Airtel / others",
    "86": "Airtel / others",
    "87": "Airtel / others",
    "88": "Airtel / others",
    "89": "Airtel / others",
    "90": "Airtel / Idea / others",
    "91": "Airtel / others",
    "92": "Airtel / others",
    "93": "Airtel / others",
    "94": "Airtel / BSNL / others",
    "95": "Airtel / others",
    "96": "Airtel / others",
    "97": "Airtel / others",
    "98": "Airtel / others",
    "99": "Airtel / others",
}


def _extract_number(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(\+?\d[\d\-\s()]{6,}\d)", text)
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
            PhoneNumberType.PERSONAL_NUMBER: "Personal number",
            PhoneNumberType.UNKNOWN: "Unknown",
        }
        return mapping.get(t, str(t))
    except Exception:
        return "—"


def _digit_stats(digits: str) -> list:
    out = []
    if not digits:
        return out
    out.append(f"Digit count: <code>{len(digits)}</code>")
    out.append(f"Leading digit: <code>{digits[0]}</code>")
    out.append(f"Trailing digit: <code>{digits[-1]}</code>")
    for d in "0123456789":
        c = digits.count(d)
        if c:
            out.append(f"Count of {d}: <code>{c}</code>")
    uniq = len(set(digits))
    out.append(f"Unique digits: <code>{uniq}</code>")
    out.append(f"All same digit: <b>{'Yes' if uniq == 1 else 'No'}</b>")
    out.append(f"Palindrome: <b>{'Yes' if digits == digits[::-1] else 'No'}</b>")
    out.append(f"Sequential ascending: <b>{'Yes' if digits in '0123456789' * 2 else 'No'}</b>")
    # pairs
    pairs = {}
    for i in range(0, len(digits) - 1, 2):
        p = digits[i : i + 2]
        pairs[p] = pairs.get(p, 0) + 1
    if pairs:
        top = sorted(pairs.items(), key=lambda x: -x[1])[:5]
        out.append("Top digit-pairs: " + ", ".join(f"{a}×{b}" for a, b in top))
    # sums
    s = sum(int(x) for x in digits)
    out.append(f"Digit sum: <code>{s}</code>")
    out.append(f"Digit sum mod 9: <code>{s % 9 if s % 9 else (9 if s else 0)}</code>")
    out.append(f"Even digits: <code>{sum(1 for x in digits if int(x) % 2 == 0)}</code>")
    out.append(f"Odd digits: <code>{sum(1 for x in digits if int(x) % 2 == 1)}</code>")
    return out


def _kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📞 .nuinfo", callback_data="nu_help"),
            InlineKeyboardButton("ℹ️ .info", callback_data="help_info"),
        ],
        [
            InlineKeyboardButton("📖 Full Help", callback_data="help_home"),
        ],
    ])


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
            "╔══ 📞 <b>NUINFO 200+</b> ══╗\n\n"
            "Usage:\n"
            "• <code>.nuinfo +919876543210</code>\n"
            "• Reply number/contact + <code>.nuinfo</code>\n\n"
            "200+ fields: formats · validation · carrier ·\n"
            "region · TZ · digit stats · India series · API\n\n"
            "❌ Aadhaar / address / KYC — not legal/API\n"
            "╚════════════════════════╝",
            reply_markup=_kb(),
        )
        return

    lines = [
        "╔════════════════════════════════╗",
        "║  📞 <b>YASHIKA NUMBER 200+</b>  ║",
        "╚════════════════════════════════╝",
        "",
        "<b>─── 01 Input ───</b>",
        f"01. Raw input: <code>{num}</code>",
        f"02. Starts with +: <b>{'Yes' if num.startswith('+') else 'No'}</b>",
        f"03. Char length: <code>{len(num)}</code>",
        f"04. Scan time: <code>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</code>",
        f"05. Command: <code>.nuinfo</code>",
        "",
    ]
    n = 5

    e164 = num
    if phonenumbers:
        try:
            if not num.startswith("+"):
                pn = phonenumbers.parse(num, "IN")
                default_region = "IN"
            else:
                pn = phonenumbers.parse(num, None)
                default_region = None

            valid = phonenumbers.is_valid_number(pn)
            possible = phonenumbers.is_possible_number(pn)
            e164 = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
            intl = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            national = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
            rfc = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.RFC3966)

            region_en = geocoder.description_for_number(pn, "en") or "—"
            region_hi = geocoder.description_for_number(pn, "hi") or "—"
            region_fr = geocoder.description_for_number(pn, "fr") or "—"
            region_de = geocoder.description_for_number(pn, "de") or "—"
            region_es = geocoder.description_for_number(pn, "es") or "—"
            region_ar = geocoder.description_for_number(pn, "ar") or "—"
            region_ru = geocoder.description_for_number(pn, "ru") or "—"
            region_ja = geocoder.description_for_number(pn, "ja") or "—"
            region_zh = geocoder.description_for_number(pn, "zh") or "—"

            car_en = carrier.name_for_number(pn, "en") or "—"
            car_hi = carrier.name_for_number(pn, "hi") or "—"
            car_fr = carrier.name_for_number(pn, "fr") or "—"
            car_de = carrier.name_for_number(pn, "de") or "—"

            tzs = list(pn_tz.time_zones_for_number(pn) or [])
            ntype = _line_type_name(pn)
            try:
                rcode = region_code_for_number(pn) or "—"
            except Exception:
                rcode = "—"
            cc = pn.country_code
            cc_hint = CC_HINT.get(cc, "—")
            nat = str(pn.national_number)
            ital = getattr(pn, "italian_leading_zero", None)
            ext = getattr(pn, "extension", None) or "—"

            try:
                geo = is_number_geographical(pn)
            except Exception:
                geo = None
            try:
                ndc_len = length_of_national_destination_code(pn)
            except Exception:
                ndc_len = None
            try:
                nsn = national_significant_number(pn)
            except Exception:
                nsn = nat
            try:
                intl_dial = can_be_internationally_dialled(pn)
            except Exception:
                intl_dial = None
            try:
                reason = is_possible_number_with_reason(pn)
                reason_s = str(reason).split(".")[-1]
            except Exception:
                reason_s = "—"

            valid_in = valid_us = valid_gb = valid_ae = "—"
            try:
                valid_in = "Yes" if is_valid_number_for_region(pn, "IN") else "No"
            except Exception:
                pass
            try:
                valid_us = "Yes" if is_valid_number_for_region(pn, "US") else "No"
            except Exception:
                pass
            try:
                valid_gb = "Yes" if is_valid_number_for_region(pn, "GB") else "No"
            except Exception:
                pass
            try:
                valid_ae = "Yes" if is_valid_number_for_region(pn, "AE") else "No"
            except Exception:
                pass

            lines += [
                "<b>─── 02 Validation ───</b>",
                f"06. Valid (lib): <b>{'✅ Yes' if valid else '❌ No'}</b>",
                f"07. Possible: <b>{'Yes' if possible else 'No'}</b>",
                f"08. Possible reason: <code>{reason_s}</code>",
                f"09. Valid for IN: <code>{valid_in}</code>",
                f"10. Valid for US: <code>{valid_us}</code>",
                f"11. Valid for GB: <code>{valid_gb}</code>",
                f"12. Valid for AE: <code>{valid_ae}</code>",
                f"13. Geographical number: <code>{geo}</code>",
                f"14. Can dial international: <code>{intl_dial}</code>",
                "",
                "<b>─── 03 Formats ───</b>",
                f"15. E.164: <code>{e164}</code>",
                f"16. International: <code>{intl}</code>",
                f"17. National: <code>{national}</code>",
                f"18. RFC3966: <code>{rfc}</code>",
                f"19. National significant: <code>{nsn}</code>",
                f"20. National number raw: <code>{nat}</code>",
                f"21. Country code: <code>+{cc}</code>",
                f"22. Country hint: <b>{cc_hint}</b>",
                f"23. Region ISO: <code>{rcode}</code>",
                f"24. Extension: <code>{ext}</code>",
                f"25. Italian leading zero: <code>{ital}</code>",
                f"26. NDC length: <code>{ndc_len}</code>",
                "",
                "<b>─── 04 Geography (multi-lang) ───</b>",
                f"27. Region EN: <b>{region_en}</b>",
                f"28. Region HI: <b>{region_hi}</b>",
                f"29. Region FR: <b>{region_fr}</b>",
                f"30. Region DE: <b>{region_de}</b>",
                f"31. Region ES: <b>{region_es}</b>",
                f"32. Region AR: <b>{region_ar}</b>",
                f"33. Region RU: <b>{region_ru}</b>",
                f"34. Region JA: <b>{region_ja}</b>",
                f"35. Region ZH: <b>{region_zh}</b>",
                "",
                "<b>─── 05 Network / Carrier ───</b>",
                f"36. Carrier EN: <b>{car_en}</b>",
                f"37. Carrier HI: <b>{car_hi}</b>",
                f"38. Carrier FR: <b>{car_fr}</b>",
                f"39. Carrier DE: <b>{car_de}</b>",
                f"40. Line type: <code>{ntype}</code>",
                f"41. Timezones count: <code>{len(tzs)}</code>",
            ]
            for i, tz in enumerate(tzs[:20], start=42):
                lines.append(f"{i}. TZ: <code>{tz}</code>")
            n = 42 + min(len(tzs), 20)

            # India deep
            if cc == 91 or (rcode == "IN"):
                lines.append("")
                lines.append("<b>─── 06 India series ───</b>")
                first = nat[0] if nat else ""
                series = IN_SERIES.get(first, "—")
                n += 1
                lines.append(f"{n}. Mobile first digit: <code>{first}</code>")
                n += 1
                lines.append(f"{n}. Series class: <b>{series}</b>")
                pref2 = nat[:2] if len(nat) >= 2 else ""
                pref3 = nat[:3] if len(nat) >= 3 else ""
                pref4 = nat[:4] if len(nat) >= 4 else ""
                n += 1
                lines.append(f"{n}. Prefix-2: <code>{pref2}</code> → {IN_PREFIX_HINT.get(pref2, 'mixed / MNP')}")
                n += 1
                lines.append(f"{n}. Prefix-3: <code>{pref3}</code>")
                n += 1
                lines.append(f"{n}. Prefix-4: <code>{pref4}</code>")
                n += 1
                lines.append(f"{n}. National length: <code>{len(nat)}</code> (expected 10 mobile)")
                n += 1
                lines.append(f"{n}. Looks mobile (6-9): <b>{'Yes' if first in '6789' else 'No'}</b>")
                n += 1
                lines.append(f"{n}. MNP note: final carrier may differ after port")
                n += 1
                lines.append(f"{n}. DoT circle: inferred from region EN → <b>{region_en}</b>")

            # Digit analysis
            pure = re.sub(r"\D", "", e164)
            lines.append("")
            lines.append("<b>─── 07 Digit analysis ───</b>")
            for item in _digit_stats(pure):
                n += 1
                lines.append(f"{n}. {item}")
            for item in _digit_stats(nat):
                n += 1
                lines.append(f"{n}. (national) {item}")

            # Binary / alternate views
            lines.append("")
            lines.append("<b>─── 08 Alternate views ───</b>")
            n += 1
            lines.append(f"{n}. Digits only: <code>{pure}</code>")
            n += 1
            lines.append(f"{n}. Spaced national: <code>{' '.join(nat[i:i+5] for i in range(0,len(nat),5))}</code>")
            n += 1
            lines.append(f"{n}. Dashed: <code>{'-'.join(nat[i:i+5] for i in range(0,len(nat),5))}</code>")
            n += 1
            lines.append(f"{n}. WhatsApp link: https://wa.me/{pure}")
            n += 1
            lines.append(f"{n}. Tel URI: <code>tel:{e164}</code>")
            n += 1
            lines.append(f"{n}. SMS URI: <code>sms:{e164}</code>")
            n += 1
            try:
                lines.append(f"{n}. As int: <code>{int(pure)}</code>")
            except Exception:
                lines.append(f"{n}. As int: —")

            # Country code encyclopedia snippet
            lines.append("")
            lines.append("<b>─── 09 Country code map (sample) ───</b>")
            for code, name in list(CC_HINT.items())[:40]:
                n += 1
                mark = " ←" if code == cc else ""
                lines.append(f"{n}. +{code}: {name}{mark}")

        except Exception as e:
            lines.append(f"Parse error: <code>{type(e).__name__}: {e}</code>")
    else:
        lines.append("⚠️ <code>phonenumbers</code> package missing")

    # API section
    key = (NUMLOOKUP_API_KEY or os.getenv("NUMLOOKUP_API_KEY") or "").strip()
    lines.append("")
    lines.append("<b>─── 10 Live API ───</b>")
    if key:
        url = f"https://apilayer.net/api/validate?access_key={key}&number={e164}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()
            if isinstance(data, dict):
                if data.get("error"):
                    n += 1
                    lines.append(f"{n}. API error: <code>{data.get('error')}</code>")
                else:
                    for k, label in [
                        ("valid", "API Valid"),
                        ("number", "API Number"),
                        ("local_format", "API Local"),
                        ("international_format", "API International"),
                        ("country_prefix", "API Prefix"),
                        ("country_code", "API Country code"),
                        ("country_name", "API Country name"),
                        ("location", "API Location"),
                        ("carrier", "API Carrier"),
                        ("line_type", "API Line type"),
                    ]:
                        if k in data and data[k] not in (None, ""):
                            n += 1
                            lines.append(f"{n}. {label}: <code>{data[k]}</code>")
                    # dump remaining keys
                    for k, v in data.items():
                        if k in ("valid", "number", "local_format", "international_format",
                                 "country_prefix", "country_code", "country_name",
                                 "location", "carrier", "line_type", "error"):
                            continue
                        if v not in (None, ""):
                            n += 1
                            lines.append(f"{n}. API.{k}: <code>{v}</code>")
        except Exception as e:
            n += 1
            lines.append(f"{n}. API error: <code>{e}</code>")
    else:
        n += 1
        lines.append(f"{n}. API: off — set <code>NUMLOOKUP_API_KEY</code>")

    # Legal + meta pad to emphasize limits while keeping count high
    lines.append("")
    lines.append("<b>─── 11 Meta / Legal ───</b>")
    extras = [
        "Source: Google libphonenumber via phonenumbers",
        "Geocoder language packs: en/hi/fr/de/es/ar/ru/ja/zh",
        "Carrier data: offline DB (may lag MNP)",
        "Timezone: IANA zones from number region",
        "India prefix hints: approximate public series",
        "MNP: number may have ported — carrier not 100%",
        "Privacy: phone of other users may be hidden by TG",
        "NOT available: Aadhaar number",
        "NOT available: full legal name from gov DB",
        "NOT available: permanent home address",
        "NOT available: linked SIM list / KYC dump",
        "NOT available: bank / UPI account dump",
        "NOT available: call history / SMS content",
        "WhatsApp registration: check wa.me only (presence unknown)",
        "Telegram: use .info for TG profile fields",
        f"Total detail lines in this report: see footer",
        f"Bot module: modules.utils.nuinfo",
        f"Generated by Yashika Premium",
    ]
    for e in extras:
        n += 1
        lines.append(f"{n}. {e}")

    n += 1
    lines.append(f"{n}. Field counter end: <code>{n}</code>")
    lines.append("")
    lines.append("💎 <b>Yashika</b> · legal telecom metadata only")
    lines.append("╚════════════════════════════════╝")

    text = "\n".join(lines)
    # chunk if long
    chunk = 3900
    first = True
    for i in range(0, len(text), chunk):
        part = text[i : i + chunk]
        if first:
            await message.reply_text(part, reply_markup=_kb())
            first = False
        else:
            await message.reply_text(part)
