<div align="center">

# ✨💎 YASHIKA PREMIUM 💎✨

### Telegram **Userbot + Bot** Hybrid · Owner-Only · Railway Ready

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=A855F7&center=true&vCenter=true&multiline=true&repeat=true&width=520&height=80&lines=Premium+Userbot+%C2%B7+Bot+Login;.+help+with+Buttons;200%2B+Info+%C2%B7+NuInfo+%C2%B7+Fun+Arts" alt="typing" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pyrogram](https://img.shields.io/badge/Kurigram%2FPyrogram-2.x-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Optional-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/Use-Personal%20Owner-FF2D55?style=for-the-badge)

[![GitHub stars](https://img.shields.io/github/stars/Kartiknishad36/yashika-?style=social)](https://github.com/Kartiknishad36/yashika-)
[![GitHub forks](https://img.shields.io/github/forks/Kartiknishad36/yashika-?style=social)](https://github.com/Kartiknishad36/yashika-)

---

### 🚀 One-Click Deploy

| Platform | Button / Link |
|:--------:|:-------------|
| **Railway** | [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template) · [railway.app/new](https://railway.app/new) |
| **Render** | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy) · [dashboard.render.com](https://dashboard.render.com/) |
| **Heroku** | [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy) · [dashboard.heroku.com](https://dashboard.heroku.com/) |
| **Koyeb** | [![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy) · [app.koyeb.com](https://app.koyeb.com/) |
| **Fly.io** | [fly.io/docs](https://fly.io/docs/hands-on/launch-app/) · [fly.io/dashboard](https://fly.io/dashboard) |
| **Vercel** | [vercel.com/new](https://vercel.com/new) *(not ideal for long worker — use for static only)* |
| **Cyclic** | [app.cyclic.sh](https://app.cyclic.sh/) |
| **Replit** | [replit.com](https://replit.com/) · Import GitHub repo |
| **GitHub Codespaces** | [github.com/codespaces](https://github.com/codespaces) |
| **DigitalOcean App** | [cloud.digitalocean.com/apps](https://cloud.digitalocean.com/apps) |
| **Google Cloud Run** | [console.cloud.google.com/run](https://console.cloud.google.com/run) |
| **AWS EC2 / Lightsail** | [console.aws.amazon.com](https://console.aws.amazon.com/) |
| **Oracle Free VPS** | [cloud.oracle.com](https://cloud.oracle.com/) |
| **Hetzner / Contabo VPS** | [hetzner.com](https://www.hetzner.com/) · [contabo.com](https://contabo.com/) |
| **Bot-Host / Daki / QmHost** | Any Python 24/7 host that supports `python main.py` |

> **Best picks for this bot:** **Railway** · **Render (Background Worker)** · **Koyeb** · **VPS**  
> Needs a **always-on worker process** (not serverless timeout).

---

</div>

## ✨ Features

<table>
<tr>
<td width="50%">

### 👑 Core
- Owner-only (`.` prefix)
- Premium **button** help menu
- Bot + Userbot hybrid
- `/login` on **bot only**
- Multi-session manager
- Auto-delete replies

</td>
<td width="50%">

### 🔥 Power
- `.info` / `.whois` full TG fields
- `.user` deep chat map → Log Group
- `.nuinfo` **200+** phone fields
- `.tagall` · `.bro` · `.clone`
- Auto-reply style scan
- VC play · Fun ASCII arts

</td>
</tr>
</table>

---

## 📦 Repo structure

```text
yashika-/
├── main.py                 # boot loader
├── config.py               # env
├── core/                   # clients · notify · autodelete · calls
├── database/               # mongo + fallback
├── modules/
│   ├── bot/                # /start /login
│   ├── owner/              # sudo · clone · tracker · sessions
│   ├── global_mod/         # tagall · bro · warn · anti*
│   ├── utils/              # help · info · nuinfo · fun
│   ├── media/              # kang · download
│   └── vc/                 # music
├── requirements.txt
├── Procfile                # worker: python3 main.py
├── Dockerfile
└── .env.example
```

---

## 🔐 Environment variables

Copy `.env.example`:

| Variable | Required | Description |
|----------|:--------:|-------------|
| `API_ID` | ✅ | [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | Telegram API hash |
| `BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | ✅ | Your numeric Telegram ID |
| `STRING_SESSION` | ⚡ | Userbot session (Pyrogram) |
| `LOG_GROUP_ID` | ⚡ | Private log group (`-100…`) |
| `MONGO_URI` | ○ | Atlas / Railway Mongo |
| `MONGO_DB` | ○ | Default `yashika` |
| `BOT_NAME` | ○ | Display name |
| `OWNER_USERNAME` | ○ | Without `@` |
| `AUTO_DELETE` | ○ | `true` / `false` |
| `DELETE_DELAY` | ○ | Seconds (e.g. `1.5`) |
| `NUMLOOKUP_API_KEY` | ○ | Optional live number API |
| `COOKIES_PATH` | ○ | YouTube cookies for music |

> Without `STRING_SESSION` → **bot-only** mode.  
> Userbot commands (`.help` on your account) need a valid session.

---

## 🛠 Local run

```bash
git clone https://github.com/Kartiknishad36/yashika-.git
cd yashika-
pip install -r requirements.txt
cp .env.example .env   # fill values
python main.py
```

---

## 🌐 Deploy guides (quick)

### 1️⃣ Railway — [railway.app](https://railway.app/)
1. **New Project** → Deploy from GitHub → select `yashika-`
2. Add variables from table above
3. Start command: `python main.py` (or use `Procfile` worker)
4. Deploy · open logs → `[READY]`

### 2️⃣ Render — [render.com](https://render.com/)
1. **New** → **Background Worker**
2. Connect repo · Runtime **Python**
3. Build: `pip install -r requirements.txt`
4. Start: `python main.py`
5. Add env vars → Create Worker

### 3️⃣ Heroku — [heroku.com](https://www.heroku.com/)
```bash
heroku create yashika-ub
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... OWNER_ID=...
heroku config:set STRING_SESSION=... LOG_GROUP_ID=...
git push heroku main
heroku ps:scale worker=1
```

### 4️⃣ Koyeb — [koyeb.com](https://www.koyeb.com/)
1. Create App → GitHub repo
2. Run command: `python main.py`
3. Instance type: free/nano · add env · Deploy

### 5️⃣ Fly.io — [fly.io](https://fly.io/)
```bash
fly launch
fly secrets set API_ID=... API_HASH=... BOT_TOKEN=... OWNER_ID=...
fly deploy
```

### 6️⃣ VPS (Ubuntu)
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git
git clone https://github.com/Kartiknishad36/yashika-.git && cd yashika-
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# screen / tmux / systemd
screen -S yashika
python main.py
```

### 7️⃣ Docker
```bash
docker build -t yashika .
docker run -d --env-file .env --name yashika yashika
```

---

## 🎮 Commands (snapshot)

| Cmd | Action |
|-----|--------|
| `.help` | **Button menu** (all categories) |
| `.ping` / `.alive` | Status + buttons |
| `.info` / `.whois` | Full Telegram user report |
| `.user` | Groups · channels · DMs → Log |
| `.nuinfo +91…` | **200+** number metadata |
| `.tagall` / `.tag` | Premium tag |
| `.bro` / `.unbro` | Roast spam |
| `.clone` / `.back` | Profile clone |
| `.autoreply on` | Style-learn reply |
| `.play` | VC music |
| `.cat` `.rose` `.moon` … | Fun arts |

**Login:** Bot private chat only → `/login` (phone → OTP → 2FA) → session to **Log Group**.

---

## 🔗 Useful links

| What | URL |
|------|-----|
| **This repo** | https://github.com/Kartiknishad36/yashika- |
| Telegram API | https://my.telegram.org |
| BotFather | https://t.me/BotFather |
| Railway | https://railway.app |
| Render | https://render.com |
| Heroku | https://heroku.com |
| Koyeb | https://koyeb.com |
| Fly.io | https://fly.io |
| MongoDB Atlas | https://www.mongodb.com/atlas |
| Pyrogram docs | https://docs.pyrogram.org |
| yt-dlp cookies | https://github.com/yt-dlp/yt-dlp/wiki/Extractors |

---

## ⚖️ Legal

`.nuinfo` uses **public** telecom metadata (libphonenumber / optional API).  
**Not implemented / not available:** Aadhaar, home address, KYC dumps, bank data.  
Use only on accounts you own. Follow Telegram ToS.

---

<div align="center">

### 💎 Yashika Premium · Personal Owner Build

<img src="https://img.shields.io/badge/Status-Online%20Ready-00C853?style=for-the-badge" />
<img src="https://img.shields.io/badge/Help-Button%20Menu-7C4DFF?style=for-the-badge" />
<img src="https://img.shields.io/badge/NuInfo-200%2B%20Fields-FF6D00?style=for-the-badge" />

**Star ⭐ the repo if it helps you**

`python main.py` · Prefix **`.`** · Owner only

</div>
