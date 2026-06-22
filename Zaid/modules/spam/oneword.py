import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from Zaid.modules.basic.profile import extract_user # Required if you want to use extraction utilities later
from Zaid import SUDO_USER # Importing SUDO_USER dynamically from your main bot config

OW_FILE = "oneword.txt"
ACTIVE_OW_TASKS = {}

@Client.on_message(
    filters.command(["ow", "oneword"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def oneword_spam(xspam: Client, e: Message):
    chat_id = e.chat.id

    # Ignore if a task is already running, or if it is not a reply to a user message
    if chat_id in ACTIVE_OW_TASKS or not e.reply_to_message or not e.reply_to_message.from_user:
        return

    # Check if the word file exists
    if not os.path.exists(OW_FILE):
        return

    # Read and split words from the file
    with open(OW_FILE, "r", encoding="utf-8") as file:
        words = file.read().split()

    # Ignore if the file is empty
    if not words:
        return

    target_user = e.reply_to_message.from_user
    user_id = target_user.id
    
    # Safety check for sudo and verified users (fetching variables dynamically from global context)
    try:
        from Zaid import VERIFIED_USERS, SUDO_USERS
        if int(user_id) in VERIFIED_USERS or int(user_id) in SUDO_USERS:
            return
    except ImportError:
        pass

    fname = target_user.first_name
    mention = f"[{fname}](tg://user?id={user_id})"

    # Register the active task and delete the command message
    ACTIVE_OW_TASKS[chat_id] = True
    await e.delete()

    # Loop through each word and send it
    for word in words:
        # Stop execution if .owstop was triggered
        if chat_id not in ACTIVE_OW_TASKS:
            break
            
        msg = f"{mention} {word}"
        try:
            await xspam.send_message(chat_id, msg)
            await asyncio.sleep(0.15) # Flood limit delay
        except Exception:
            break

    # Cleanup the task after completion or error
    if chat_id in ACTIVE_OW_TASKS:
        del ACTIVE_OW_TASKS[chat_id]


@Client.on_message(
    filters.command(["owstop", "stopow"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def stop_oneword(xspam: Client, e: Message):
    chat_id = e.chat.id
    
    # Remove the chat from active tasks to break the loop
    if chat_id in ACTIVE_OW_TASKS:
        del ACTIVE_OW_TASKS[chat_id]
        await e.delete()
