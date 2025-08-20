def send_telegram_help():
    help_text = """*Available commands:*
/remove [plugin] – remove a plugin
/status – show current status
/fakesign – fakesign all executables
/thin – thin all executables
/icon – change app icon
/extensions – remove encrypted extensions"""
    send_telegram_message(help_text, parse_mode="Markdown")

import requests
import logging

TELEGRAM_BOT_TOKEN = "<8443751831:AAGdEhivC_9BOxB_8wTMrlNpmjkTbDtp2uM>"
TELEGRAM_CHAT_ID = "<YOUR_CHAT_ID>"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram_message(text: str, parse_mode: str = "Markdown"):
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        response = requests.post(TELEGRAM_API_URL, data=data)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
