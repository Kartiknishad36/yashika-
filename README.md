# 💎 Yashika Premium Userbot

Telegram **userbot + bot** hybrid — Railway / Render ready.

## Features

- Owner-only commands (`.` prefix)
- Premium single `.help` menu
- Ultra-detail `.info` / `.user` reports
- Tagall · Bro · Clone · Auto-reply style scan
- Bot `/login` for extra sessions
- MongoDB optional + JSON fallback
- Auto-delete · VC · Fun ASCII arts

## Setup

1. Copy `.env.example` → set vars:
   - `API_ID` `API_HASH`
   - `BOT_TOKEN` (required for bot login)
   - `STRING_SESSION` (userbot)
   - `OWNER_ID` `LOG_GROUP_ID`
   - Optional: `MONGO_URI` `NUMLOOKUP_API_KEY`

2. Install:
```bash
pip install -r requirements.txt
```

3. Run:
```bash
python main.py
```

## Key commands

| Cmd | Action |
|-----|--------|
| `.help` | Full premium menu |
| `.ping` | Latency |
| `.info` | Ultra user details |
| `.user` | Full chats + log group |
| `.tagall` | Tag members |
| `.bro` | Roast spam |
| `.clone` / `.back` | Profile clone |
| `.autoreply on` | Smart reply |

**Login:** Bot DM only → `/login` (phone → OTP → 2FA)

## Legal note

Number lookup (`.nuinfo`) uses public carrier/region data only.  
Aadhaar / home address / KYC dumps are **not** available and not implemented.

## Deploy

- **Railway:** set env vars, start command `python main.py`
- **Procfile** included for worker dyno

---

Made for personal owner use · Premium style
