#!/usr/bin/env python3
"""
Telegram Chat ID Finder

This utility script helps you find the chat IDs for your Telegram groups or channels.
Run this script to get the chat IDs that you need to configure in your .env file.

Usage:
    python get_chat_id.py

Make sure your TELEGRAM_BOT_TOKEN is set in your .env file before running this script.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_chat_ids():
    """
    Fetches recent updates from Telegram API to find chat IDs.
    
    Returns:
        None: Prints chat IDs to console
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
        print("Please make sure you have created a .env file with your bot token.")
        return

    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        if not data.get("ok"):
            print(f"❌ Telegram API Error: {data.get('description', 'Unknown error')}")
            return
            
        updates = data.get("result", [])
        
        if not updates:
            print("ℹ️  No recent messages found.")
            print("💡 Tip: Send a message to your bot or add it to a group, then run this script again.")
            return
        
        print("📋 Found the following chat IDs:\n")
        print("=" * 50)
        
        seen_chats = set()
        
        for update in updates:
            message = update.get("message", {})
            chat = message.get("chat", {})
            
            if chat and chat.get("id") not in seen_chats:
                chat_id = chat.get("id")
                chat_type = chat.get("type", "unknown")
                chat_title = chat.get("title", chat.get("first_name", "Unknown"))
                
                seen_chats.add(chat_id)
                
                print(f"💬 Chat: {chat_title}")
                print(f"🆔 ID: {chat_id}")
                print(f"📝 Type: {chat_type}")
                print("-" * 30)
        
        if seen_chats:
            print("\n✅ Copy the chat IDs you need and add them to your .env file:")
            print("TELEGRAM_CHAT_IDS=chat_id_1,chat_id_2,chat_id_3")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        print("Please check your internet connection and try again.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("Please check your bot token and try again.")

if __name__ == "__main__":
    print("🤖 Telegram Chat ID Finder")
    print("=" * 30)
    get_chat_ids() 