import os
from pyrogram import Client, filters
from youtubesearchpython.__future__ import VideosSearch
import time
import re
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Your bot token
API_ID = 14254903
API_HASH = '6215310c3d291816386475a3f17fe970'

BOT_TOKEN = "7505403312:AAH1ePb12fU5epQczzVlak2Y1uO9xUVRxkE"

# Initialize the Pyrogram client
app = Client("youtube_search_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to search YouTube for video IDs using VideoSearch
async def search_youtube(query, max_results=1000):
    search = VideoSearch(query, limit=max_results)
    video_ids = set()

    while len(video_ids) < max_results and search.next():
        for result in search.result()["result"]:
            title = result["title"]
            video_id = result["id"]
            if video_id:
                # Print the title to the console
                print(f"Found: {title}")
                # Add the video ID to the set
                video_ids.add(video_id)
            
            if len(video_ids) >= max_results:
                break
    
    return list(video_ids)

@app.on_message(filters.command("search") & filters.private)
async def search_command(client, message):
    # Extract the query from the message
    query = " ".join(message.command[1:])
    if not query:
        await message.reply_text("Please provide a query to search for.")
        return
    
    await message.reply_text(f"Searching for '{query}' on YouTube...")

    # Perform the search
    video_ids = await search_youtube(query)
    
    # Save the video IDs to a file
    with open("names.txt", "w") as file:
        file.write("\n".join(video_ids))
    
    # Send the file to the user
    await message.reply_document("names.txt")
    
    # Clean up the file after sending
    os.remove("names.txt")

if __name__ == "__main__":
    app.run()
