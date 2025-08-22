import os
import time
import requests
import subprocess
import logging
from cyan.telegram_utils import send_telegram_message, send_telegram_help

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
LAST_UPDATE_ID = 0

# --- Command Handler Functions ---

def handle_zsign(chat_id, args):
    """
    Handles a request to sign a file using the convert_to_cyan.py script.
    This is a placeholder and requires you to have your signing config ready.
    """
    if not args:
        send_telegram_message(chat_id, "Usage: `/zsign [path_to_inject_file]`\nExample: `/zsign tweaks/MyTweak.dylib`")
        return

    inject_file = args[0]
    send_telegram_message(chat_id, f"Received request to sign `{inject_file}`. This is a placeholder and is not yet implemented.")
    #
    # TODO: Implement the logic to call your convert_to_cyan.py script
    # Example:
    # try:
    #     # Note: This assumes the script can get the password non-interactively
    #     result = subprocess.run(['python3', 'convert_to_cyan.py', inject_file], check=True, capture_output=True, text=True)
    #     send_telegram_message(chat_id, f"Successfully signed:\n```\n{result.stdout}\n```")
    # except subprocess.CalledProcessError as e:
    #     send_telegram_message(chat_id, f"Failed to sign:\n```\n{e.stderr}\n```")
    #

def handle_udid(chat_id, args):
    """
    Placeholder for handling UDID registration.
    """
    if not args:
        send_telegram_message(chat_id, "Usage: `/udid [your_device_udid]`")
        return
    
    udid = args[0]
    send_telegram_message(chat_id, f"Received UDID `{udid}`. UDID registration is not yet implemented.")
    #
    # TODO: Implement Apple Developer API logic here. This is complex and requires API keys.
    #

def handle_git_pull(chat_id, args):
    """
    Runs 'git pull' to update the repository.
    """
    send_telegram_message(chat_id, "Attempting to pull latest changes from GitHub...")
    try:
        result = subprocess.run(['git', 'pull'], check=True, capture_output=True, text=True)
        send_telegram_message(chat_id, f"Update successful:\n```\n{result.stdout}\n```")
    except subprocess.CalledProcessError as e:
        send_telegram_message(chat_id, f"Failed to pull updates:\n```\n{e.stderr}\n```")

# --- Main Bot Loop ---

def get_updates(offset):
    """Polls Telegram for new messages."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("result", [])
    except requests.RequestException as e:
        logging.error(f"Error getting updates: {e}")
        return []

def main():
    """Main function to run the bot."""
    global LAST_UPDATE_ID
    if not TELEGRAM_BOT_TOKEN:
        logging.error("FATAL: TELEGRAM_BOT_TOKEN environment variable is not set.")
        return

    logging.info("Bot started...")
    while True:
        updates = get_updates(LAST_UPDATE_ID + 1)
        if updates:
            for update in updates:
                LAST_UPDATE_ID = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    message_data = update["message"]
                    chat_id = message_data["chat"]["id"]
                    message_text = message_data["text"]
                    
                    logging.info(f"Received message from chat_id {chat_id}: {message_text}")

                    if message_text.startswith('/'):
                        parts = message_text.split()
                        command = parts[0]
                        args = parts[1:]

                        if command == "/start" or command == "/help":
                            send_telegram_help(chat_id)
                        elif command == "/zsign":
                            handle_zsign(chat_id, args)
                        elif command == "/udid":
                            handle_udid(chat_id, args)
                        elif command == "/git_pull":
                            handle_git_pull(chat_id, args)
                        else:
                            send_telegram_message(chat_id, f"Unknown command: `{command}`. Use /help to see available commands.")
        time.sleep(1)

if __name__ == "__main__":
    main()