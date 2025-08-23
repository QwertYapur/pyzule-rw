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


def is_admin_user(chat_id: str) -> bool:
    """Check if the user is an admin based on their chat_id."""
    admin_chat_ids = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "").split(",")
    return str(chat_id) in admin_chat_ids

def is_supporter_user(chat_id: str) -> bool:
    """Check if the user is a supporter based on their chat_id."""
    supporter_chat_ids = os.environ.get("TELEGRAM_SUPPORTER_CHAT_ID", "").split(",")
    return str(chat_id) in supporter_chat_ids

def is_owner_user(chat_id: str) -> bool:
    """Check if the user is the owner based on their chat_id."""
    owner_chat_ids = os.environ.get("TELEGRAM_OWNER_CHAT_ID", "").split(",")
    return str(chat_id) in owner_chat_ids

def get_user_privilege_level(chat_id: str) -> str:
    """Get the user's privilege level: 'owner', 'admin', 'supporter', or 'user'."""
    if is_owner_user(chat_id):
        return 'owner'
    elif is_admin_user(chat_id):
        return 'admin'
    elif is_supporter_user(chat_id):
        return 'supporter'
    else:
        return 'user'

def send_telegram_help(chat_id: str):
    """Sends a privilege-based help message to the specified Telegram chat."""
    privilege_level = get_user_privilege_level(chat_id)
    
    # Basic commands available to all users
    help_text = r"""🤖 *pyzule-rw Bot Commands*

📱 *Device Management*
/udid \[device\_udid\] - Register device UDID for development signing

🔐 *Signing Operations*
/zsign \[ipa\_file\] - Sign IPA with development certificate using zsign

/help - Show this help message

"""
    
    # Supporter and above commands
    if privilege_level in ['supporter', 'admin', 'owner']:
        help_text += r"""🔧 *Plugin Management* \(Supporter\+\)
/plugins - List and manage app plugins/extensions
/plugins \[ipa\_file\] - Show plugins for specific IPA file

"""
    
    # Admin and above commands
    if privilege_level in ['admin', 'owner']:
        help_text += r"""⚙️ *System Commands* \(Admin\+\)
/git\_pull - Pull latest updates from GitHub
/users - View user statistics

*Legacy Commands* \(Admin\+\)
/remove \[plugin\] – remove a plugin
/status – show current status
/fakesign – fakesign all executables
/thin – thin all executables
/icon – change app icon
/extensions – remove encrypted extensions

"""
    
    # Owner-only commands
    if privilege_level == 'owner':
        help_text += r"""👑 *Owner Commands* \(Owner Only\)
/payments - View payment history and statistics
/upgrade \[chat\_id\] \[tier\] - Upgrade user access level
/downgrade \[chat\_id\] - Downgrade user access level
/revenue - View revenue analytics
/billing - Manage billing and subscriptions
/whitelist \[chat\_id\] - Add user to whitelist
/blacklist \[chat\_id\] - Block user access

"""
    elif privilege_level == 'admin':
        help_text += r"""⚡ *You have Admin access\!*
Admins can manage system operations and user support\.

"""
    elif privilege_level == 'supporter':
        help_text += r"""💎 *You have Supporter access\!*
Supporters get plugin management capabilities and priority support\.

"""
    else:
        help_text += r"""💡 *Want More Features?*
• 💎 *Supporter*: Plugin management \+ priority support
• ⚡ *Admin*: System management \+ user support
• 👑 *Owner*: Full access \+ payment management

Contact an administrator for access upgrades\.

"""
    
    # Examples section
    help_text += r"""*Examples*
• `/udid 00008030-000A1D0E3EE0802E12345678` - Register iPhone UDID
• `/zsign /path/to/MyApp.ipa` - Sign IPA file"""
    
    if privilege_level in ['supporter', 'admin', 'owner']:
        help_text += r"""
• `/plugins` - View available plugins
• `/plugins /path/to/App.ipa` - Manage app plugins"""
    
    if privilege_level in ['admin', 'owner']:
        help_text += r"""
• `/git_pull` - Update bot to latest version
• `/users` - View user statistics"""
    
    if privilege_level == 'owner':
        help_text += r"""
• `/payments` - View payment analytics
• `/upgrade 123456789 supporter` - Upgrade user to supporter"""
    
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
