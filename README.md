<p align="center">
  <img src="https://img.shields.io/badge/YASHIKA-PREMIUM%20USERBOT-FFD700?style=for-the-badge&logo=telegram&logoColor=black"/>
</p>

<h1 align="center">✨ 𝐘𝐀𝐒𝐇𝐈𝐊𝐀 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 ✨</h1>

<p align="center">
  <b>👑 Pure Userbot • Music • Mod • Fun 👑</b><br>
  <i>No bot token required — everything runs on your account</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-FFD700?style=flat-square&logo=python&logoColor=black"/>
  <img src="https://img.shields.io/badge/Kurigram-2.x-FFD700?style=flat-square"/>
  <img src="https://img.shields.io/badge/PyTgCalls-2.x-FFD700?style=flat-square"/>
  <img src="https://img.shields.io/badge/Mode-Userbot%20Only-gold?style=flat-square"/>
</p>

---

## 👑 About

**Yashika** is a **pure userbot** (no BotFather bot):

- 🎵 Voice chat music / video (yt-dlp + cookies)
- 🛡 PM Guard, anti-spam, secret log
- 👮 Group moderation & global ban
- 🎮 Games • Economy • Fun
- 🔥 Raid / spam / tagall / bro auto-reply
- 🔑 Owner + sudo system

> **Powered by Kartik Nishad** ⚡

---

## 🚀 Deploy

### VPS / Local

```bash
git clone https://github.com/Kartiknishad36/yashika-.git
cd yashika-
pip install -r requirements.txt
cp .env.example .env
# edit .env — STRING_SESSION required (no BOT_TOKEN)
python3 main.py
```

### Platforms

Railway / Heroku / Koyeb / Render — same env vars as below.

---

## ⚙️ Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From my.telegram.org |
| `STRING_SESSION` | ✅ | Your user account session string |
| `OWNER_ID` | ✅ | Your Telegram numeric ID |
| `ASSISTANT_SESSION` | ⭐ | Optional 2nd account for VC |
| `COOKIES_PATH` | ⭐ | `cookies.txt` for YouTube |
| `GEMINI_API_KEY` | ⭐ | Optional AI |
| `LOG_GROUP_ID` | ⭐ | Logs group |

**`BOT_TOKEN` is NOT used.** Pure userbot mode.

> ⚠️ Never commit `.env`, `cookies.txt`, or `*.session`.

---

## 📋 Commands (userbot prefixes `.` `!`)

| Category | Commands |
|----------|----------|
| 🎵 Music | `.play` `.vply` `.skip` `.stop` |
| 👑 Owner | `.addsudo` `.approve` |
| 🛡 PM | `.verify` `.antispam` `.secretlog` |
| 🔥 Raid | `.raid` `.spam` |
| 💕 Bro | `.bro` `.brodm` `.brogroup` |
| 🎮 Fun | `.couple` `.dice` |
| 💰 Economy | `.bal` `.daily` `.rob` |

---

## 📁 Structure

```
yashika-/
├── main.py
├── config.py
├── core/           # clients (userbot + optional assistant), call_manager
├── database/
└── modules/
    ├── owner/      # sudo, pmguard, raid…
    ├── global_mod/ # mod, bro, tagall…
    ├── vc/         # music play / controls
    ├── utils/
    ├── media/
    ├── games/
    └── economy/
```

---

## 🔗 Links

- **Repo:** [github.com/Kartiknishad36/yashika-](https://github.com/Kartiknishad36/yashika-)
- **Support:** [Group](https://t.me/+Ml99kT7JCMo0OTdl)
- **Updates:** [Channel](https://t.me/ye_duniya_ek_sapna_he)
- **Owner:** [Kartik Nishad](https://t.me/KARTIK_NISHAD_3)

---

<p align="center"><b>Pure Userbot • Made by Kartik Nishad ⚡</b></p>
