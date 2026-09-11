"""
Voice tools (userbot):
  .tts <text>     — text → voice note (gTTS)
  .stt            — reply to voice/audio → text (Google free STT)

Deps (optional):
  pip install gTTS SpeechRecognition pydub
  system: ffmpeg
"""
import os
import tempfile
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


@app.on_message(filters.command(["tts", "voice"], prefixes=PREFIXES))
@sudo_only
async def tts_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text(
            "Usage: `.tts namaste kaise ho`\n"
            "Lang auto: Hindi/English mix → try `hi` default for Devanagari."
        )
        return

    text = parts[1].strip()[:500]
    # simple lang guess
    lang = "hi" if any("\u0900" <= ch <= "\u097F" for ch in text) else "en"

    st = await message.reply_text("🗣 Generating voice...")
    path = None
    try:
        from gtts import gTTS

        def _make():
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.close()
            gTTS(text=text, lang=lang).save(tmp.name)
            return tmp.name

        path = await asyncio.to_thread(_make)
        await client.send_audio(
            message.chat.id,
            path,
            caption=f"🗣 {text[:100]}",
            title="TTS",
            performer="Yashika",
        )
        # also as voice note-ish: send_voice needs ogg — mp3 as audio is fine
        await st.delete()
    except ImportError:
        await st.edit_text("❌ Install: `pip install gTTS`")
    except Exception as e:
        await st.edit_text(f"❌ `{e}`")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


@app.on_message(filters.command(["stt", "transcribe"], prefixes=PREFIXES))
@sudo_only
async def stt_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not (r.voice or r.audio or r.video_note):
        await message.reply_text("Reply to a **voice / audio / video note** with `.stt`")
        return

    st = await message.reply_text("🎧 Transcribing...")
    ogg = None
    wav = None
    try:
        import speech_recognition as sr

        media = r.voice or r.audio or r.video_note
        ogg = await client.download_media(media)
        if not ogg:
            await st.edit_text("❌ Download fail.")
            return

        # convert to wav via ffmpeg
        wav = ogg + ".wav"

        def _convert():
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-i", ogg, "-ar", "16000", "-ac", "1", wav],
                check=True,
                capture_output=True,
            )

        await asyncio.to_thread(_convert)

        def _recognize():
            recog = sr.Recognizer()
            with sr.AudioFile(wav) as source:
                audio = recog.record(source)
            try:
                return recog.recognize_google(audio, language="hi-IN")
            except Exception:
                return recog.recognize_google(audio, language="en-US")

        text = await asyncio.to_thread(_recognize)
        await st.edit_text(f"📝 <b>STT</b>\n\n{text}")
    except ImportError:
        await st.edit_text(
            "❌ Install:\n`pip install SpeechRecognition pydub`\n+ ffmpeg"
        )
    except Exception as e:
        await st.edit_text(f"❌ `{e}`")
    finally:
        for p in (ogg, wav):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
