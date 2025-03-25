import os
import asyncio
import yt_dlp
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

# 🎵 Telegram API Credentials
API_ID = 26413399
API_HASH = "24775df5997c0272c42e8d5f9516e033"
BOT_TOKEN = "7612325658:AAH3Ut0jsVjhnV-aHJDpOWFETvKN3SVSvLI"

# 🔥 Initialize Bot & Voice Call
app = Client("music_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

# ✅ Allowed Admins
ADMINS = [123456789, 987654321]  # Replace with Admin User IDs

# 🎶 Playlist Queue
playlist = []

# 📢 Broadcast List (Add Group & Channel IDs)
BROADCAST_LIST = [-100123456789, -100987654321]  # Replace with Group/Channel IDs

# 🎵 Welcome Message with Buttons
WELCOME_MSG = """
🎵 **Welcome to the Ultimate Music & Video Bot!** 🎶

🔥 **Features:**  
✅ Auto Playlist + Direct YouTube/Spotify Streaming  
✅ Live Video Streaming Support  
✅ Full Admin Control (Play, Pause, Skip, Stop)  
✅ Broadcast System for Messages, Images, Videos  

🔗 **Join Our Community for More Updates!** 👇
"""

WELCOME_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Join Our Group", url="https://t.me/yourgroup")],
    [InlineKeyboardButton("🎵 Admin Channel", url="https://t.me/yourchannel")]
])

# 🎵 Extract YouTube Audio Stream URL
def get_audio_url(video_url):
    ydl_opts = {"format": "bestaudio", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info["url"], info["title"]

# 🎶 Auto Playlist System
async def play_next(chat_id):
    if playlist:
        next_url, user = playlist.pop(0)
        audio_url, title = get_audio_url(next_url)
        await call.start(chat_id)
        await call.play(chat_id, AudioPiped(audio_url))
        await app.send_photo(
            chat_id, "https://example.com/music-image.jpg",  # Replace with Music Image URL
            caption=f"🎶 **Now Playing:** {title}\n👤 **Requested by:** {user}"
        )

# 🎵 Play Music Command
@app.on_message(filters.command("play"))
async def play_music(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to control playback!")

    chat_id = message.chat.id
    url = message.text.split(" ", 1)[1]  

    audio_url, title = get_audio_url(url)

    if not playlist:
        await call.start(chat_id)
        await call.play(chat_id, AudioPiped(audio_url))
        await message.reply_photo(
            "https://example.com/music-image.jpg",  # Replace with a cool image
            caption=f"🎶 **Now Playing:** {title}\n👤 **Requested by:** {message.from_user.first_name}\n\n🔘 /pause 🔘 /resume 🔘 /skip 🔘 /stop"
        )
    else:
        playlist.append((url, message.from_user.first_name))
        await message.reply(f"📥 **Added to Playlist:** {title} 🎵\n🔄 **Position in Queue:** {len(playlist)}")

# ⏸ Pause Music
@app.on_message(filters.command("pause"))
async def pause_music(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to control playback!")

    await call.pause_stream(message.chat.id)
    await message.reply("⏸ **Music Paused!**")

# 🔁 Resume Music
@app.on_message(filters.command("resume"))
async def resume_music(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to control playback!")

    await call.resume_stream(message.chat.id)
    await message.reply("🔁 **Music Resumed!**")

# ⏭ Skip Track
@app.on_message(filters.command("skip"))
async def skip_music(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to control playback!")

    await call.stop(message.chat.id)
    await message.reply("⏭ **Skipped to Next Track!**")
    await play_next(message.chat.id)  

# ⏹ Stop Music
@app.on_message(filters.command("stop"))
async def stop_music(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to control playback!")

    playlist.clear()
    await call.stop(message.chat.id)
    await message.reply("⏹ **Music Stopped & Queue Cleared!**")

# 🎤 Broadcast System
@app.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(client, message):
    text = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else None
    reply = message.reply_to_message

    if not text and not reply:
        return await message.reply("⚠️ **Please provide a message or reply to a media file!**")

    sent_count = 0
    failed_count = 0

    for chat_id in BROADCAST_LIST:
        try:
            if text:
                await app.send_message(chat_id, f"📢 **Broadcast:**\n\n{text}")
            elif reply:
                if reply.photo:
                    await app.send_photo(chat_id, reply.photo.file_id, caption="📢 **Broadcast:**")
                elif reply.video:
                    await app.send_video(chat_id, reply.video.file_id, caption="📢 **Broadcast:**")
                elif reply.audio:
                    await app.send_audio(chat_id, reply.audio.file_id, caption="📢 **Broadcast:**")
                elif reply.document:
                    await app.send_document(chat_id, reply.document.file_id, caption="📢 **Broadcast:**")
            sent_count += 1
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")
            failed_count += 1

    await message.reply(f"✅ **Broadcast Sent to {sent_count} Groups/Channels!**\n❌ **Failed: {failed_count}**")

# 🚀 Start Bot
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for member in message.new_chat_members:
        await message.reply_photo(
            "https://example.com/welcome-music.jpg",  # Replace with a welcome image
            caption=WELCOME_MSG,
            reply_markup=WELCOME_BUTTONS
        )

async def main():
    await app.start()
    print("🎶 **Music & Video Bot Running!** 🚀")
    await asyncio.sleep(100000)

asyncio.run(main())
