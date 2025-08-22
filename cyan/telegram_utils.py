import os
import requests
import logging

# --- Configuration ---
# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load credentials from environment variables for security
# Ensure these are set in your environment before running the script
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# This is now used as a fallback or for testing purposes
TELEGRAM_ADMIN_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# --- Core Functions ---

def send_telegram_message(chat_id: str, text: str, parse_mode: str = "Markdown"):
    """
    Sends a message to a specified Telegram chat.

    Reads the bot token from environment variables.
    Logs an error if the token is not set or if the request fails.
    """
    if not TELEGRAM_BOT_TOKEN:
        logging.error("Error: TELEGRAM_BOT_TOKEN environment variable must be set.")
        return

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(api_url, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        logging.info(f"Successfully sent Telegram message to chat_id: {chat_id}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")


def send_telegram_help(chat_id: str):
    """Sends a pre-defined help message to the specified Telegram chat."""
    help_text = """*Available commands:*
/zsign [file] - Sign an inject file.
/udid [udid] - Register a device UDID (Not Implemented).
/git_pull - Pull the latest updates from GitHub.
/help - Show this help message.

*Legacy Commands:*
/remove [plugin] – remove a plugin
/status – show current status
/fakesign – fakesign all executables
/thin – thin all executables
/icon – change app icon
/extensions – remove encrypted extensions"""
    send_telegram_message(chat_id, help_text, parse_mode="Markdown")


# --- Example Usage ---

if __name__ == "__main__":
    # This block allows you to test the script directly.
    # To use it, set your environment variables first:
    # export TELEGRAM_BOT_TOKEN="your_actual_token"
    # export TELEGRAM_CHAT_ID="your_actual_chat_id"
    # Then run: python3 cyan/telegram_utils.py
    
    if TELEGRAM_ADMIN_CHAT_ID:
        print("Sending test help message to admin Telegram chat...")
        send_telegram_help(TELEGRAM_ADMIN_CHAT_ID)
    else:
        print("TELEGRAM_CHAT_ID environment variable not set. Skipping test message.")
