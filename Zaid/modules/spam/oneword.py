import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

OW_FILE = "oneword.txt"
ACTIVE_OW_TASKS = {}

@Client.on_message(
    filters.command(["ow", "oneword"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def oneword_spam(xspam: Client, e: Message):
    chat_id = e.chat.id

    # Ignore if a task is already running, or if it is not a reply to a message
    if chat_id in ACTIVE_OW_TASKS or not e.reply_to_message:
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

    reply_to_msg_id = e.reply_to_message.id

    # Register the active task and delete the command message
    ACTIVE_OW_TASKS[chat_id] = True
    await e.delete()

    # Loop through each word and send it as a direct reply
    for word in words:
        # Stop execution if .owstop was triggered
        if chat_id not in ACTIVE_OW_TASKS:
            break
            
        try:
            # Removed mention, now it only sends the word replying to the target message ID
            await xspam.send_message(chat_id, word, reply_to_message_id=reply_to_msg_id)
            await asyncio.sleep(0.01) # Reduced delay for maximum speed
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
