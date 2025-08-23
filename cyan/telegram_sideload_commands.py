# --- Sideloading Command Handlers ---
from cyan.telegram_utils import send_telegram_message, send_telegram_photo
import logging
import os

# Function to send a photo via Telegram (will be implemented later)
def send_telegram_photo(chat_id, photo_data, caption=None):
    """Send a photo to a Telegram chat."""
    from cyan.telegram_utils import send_telegram_photo as send_photo
    logging.info(f"Sending photo to {chat_id} with caption: {caption}")
    send_photo(chat_id, photo_data, caption)

def handle_sideload(chat_id, args):
    """
    Provides sideloading options and instructions for the specified IPA file.
    """
    if not args or not isinstance(args, list) or len(args) == 0:
        send_telegram_message(chat_id, """🚀 *Sideloading Options*

This command helps you install signed IPAs on your iOS device using various methods.

*Usage:* `/sideload [ipa_file_path]`

*Available Methods:*
• AltStore - No computer needed after initial setup
• Sideloadly - Requires computer for each installation
• Direct Install - Requires valid developer certificate

*Example:*
`/sideload /path/to/MyApp.ipa`""")
        return
    
    ipa_file = args[0].strip()
    
    # Validate IPA file path
    if not isinstance(ipa_file, str) or not ipa_file.lower().endswith('.ipa'):
        send_telegram_message(chat_id, "❌ Invalid file type. Please provide an IPA file.\n\n" +
                             f"Your input: `{ipa_file}`\n" +
                             "Expected: File ending with `.ipa`")
        return
    
    import os
    if not os.path.exists(ipa_file):
        send_telegram_message(chat_id, f"❌ File not found: `{ipa_file}`\n\nPlease check the file path.")
        return
    
    # Get app metadata and bundle ID
    from cyan.telegram_utils import extract_app_bundle_id, get_app_display_name
    app_bundle_id = extract_app_bundle_id(ipa_file)
    app_name = get_app_display_name(ipa_file)
    
    # Upload to Google Drive for sharing
    from cyan.drive_utils import upload_file_to_drive, get_shareable_link
    send_telegram_message(chat_id, f"⏳ *Uploading {app_name}*\n\nPreparing your app for sideloading...")
    
    try:
        file_id = upload_file_to_drive(ipa_file)
        if not file_id:
            send_telegram_message(chat_id, "❌ *Upload Failed*\n\nFailed to upload the IPA file to Google Drive.")
            return
            
        # Get shareable link
        file_url = get_shareable_link(file_id)
        
        # Generate sideloading message with options
        try:
            from cyan.sideload_utils import create_sideload_message, generate_qr_code
            
            message, keyboard = create_sideload_message(file_url, ipa_file)
            
            # Send message with inline keyboard
            send_telegram_message(chat_id, message, reply_markup=keyboard)
            
            # Generate and send QR code for direct download
            qr_buffer = generate_qr_code(file_url)
            send_telegram_photo(chat_id, qr_buffer, caption=f"📱 *Scan to download {app_name}*")
            
        except ImportError:
            # Fallback if sideload_utils is not available
            send_telegram_message(chat_id, f"""🚀 *App Ready for Sideloading*

📱 *App*: {app_name}
🆔 *Bundle ID*: {app_bundle_id}

📥 *Download Link*:
{file_url}

*Installation Options:*
• Use AltStore: Open this link on your device with AltStore installed
• Use Sideloadly: Download the IPA and use Sideloadly on your computer
• Direct Install: If you have a developer certificate""")
    
    except Exception as e:
        import logging
        logging.error(f"Error in sideload handling: {e}")
        send_telegram_message(chat_id, f"❌ *Error*\n\nAn error occurred while processing your sideload request: {str(e)}")

def handle_altstore(chat_id, args):
    """
    Generate AltStore-compatible installation links for an IPA file.
    """
    if not args or not isinstance(args, list) or len(args) == 0:
        send_telegram_message(chat_id, """🚀 *AltStore Installation*

This command generates AltStore-compatible links for installing apps.

*Usage:* `/altstore [ipa_file_path]`

*Requirements:*
• AltStore must be installed on your device
• AltServer must be running on your computer
• Your device must be on the same WiFi network as your computer

*Example:*
`/altstore /path/to/MyApp.ipa`""")
        return
    
    ipa_file = args[0].strip()
    
    # Validate IPA file path
    if not isinstance(ipa_file, str) or not ipa_file.lower().endswith('.ipa'):
        send_telegram_message(chat_id, "❌ Invalid file type. Please provide an IPA file.\n\n" +
                             f"Your input: `{ipa_file}`\n" +
                             "Expected: File ending with `.ipa`")
        return
    
    import os
    if not os.path.exists(ipa_file):
        send_telegram_message(chat_id, f"❌ File not found: `{ipa_file}`\n\nPlease check the file path.")
        return
    
    # Upload to Google Drive and generate AltStore link
    from cyan.telegram_utils import extract_app_bundle_id, get_app_display_name
    from cyan.drive_utils import upload_file_to_drive, get_shareable_link
    
    app_name = get_app_display_name(ipa_file)
    send_telegram_message(chat_id, f"⏳ *Preparing AltStore Link*\n\nUploading {app_name}...")
    
    try:
        file_id = upload_file_to_drive(ipa_file)
        if not file_id:
            send_telegram_message(chat_id, "❌ *Upload Failed*\n\nFailed to upload the IPA file to Google Drive.")
            return
            
        # Get shareable link
        file_url = get_shareable_link(file_id)
        
        # Generate AltStore URL
        try:
            from cyan.sideload_utils import generate_altstore_url, generate_qr_code
            
            altstore_url = generate_altstore_url(file_url)
            
            # Send message with AltStore link
            message = f"""🚀 *AltStore Installation Ready*

📱 *App*: {app_name}
📋 *Instructions*:
1. Make sure AltStore is installed on your device
2. Ensure AltServer is running on your computer
3. Connect to the same WiFi network
4. Click the link below to open in AltStore

📲 *AltStore Link*:
{altstore_url}

You can also download the IPA directly and add it manually to AltStore:
{file_url}"""
            
            send_telegram_message(chat_id, message)
            
            # Generate and send QR code for AltStore link
            qr_buffer = generate_qr_code(altstore_url)
            send_telegram_photo(chat_id, qr_buffer, caption=f"📱 *Scan to install {app_name} with AltStore*")
            
        except ImportError:
            # Fallback if sideload_utils is not available
            send_telegram_message(chat_id, f"""🚀 *AltStore Installation*

📱 *App*: {app_name}

📥 *Download Link*:
{file_url}

*Installation Instructions:*
1. Download the IPA on your iOS device
2. Open AltStore
3. Go to My Apps tab
4. Tap the + button
5. Select the downloaded IPA file""")
    
    except Exception as e:
        import logging
        logging.error(f"Error in altstore handling: {e}")
        send_telegram_message(chat_id, f"❌ *Error*\n\nAn error occurred while processing your AltStore request: {str(e)}")

def handle_install_status(chat_id, args):
    """
    Check installation status of apps on registered devices.
    """
    if not args or not isinstance(args, list) or len(args) == 0:
        # No arguments, show status of all apps for the user's devices
        send_telegram_message(chat_id, """📊 *App Installation Status*

To check the status of a specific app, provide its bundle ID:
`/status com.example.myapp`

To check all apps on a specific device, provide the UDID:
`/status 00008030-001E54223A38802E`

*Your Registered Devices:*
• iPhone 16 Pro (00008030-001E54223A38802E)
   - 3 apps installed, 1 expiring soon

Use `/udid` to register additional devices.""")
        return
    
    identifier = args[0].strip()
    
    try:
        # Check if this is a bundle ID or UDID
        if "." in identifier:
            # Likely a bundle ID
            from cyan.sideload_utils import check_app_status
            status = check_app_status(identifier)
            
            message = f"""📊 *App Status: {identifier}*

✅ *Installed*: {'Yes' if status['installed'] else 'No'}
🔢 *Version*: {status['version']}
⏰ *Expires*: {status['expiry']}
📅 *Days Remaining*: {status['days_remaining']}

{('⚠️ *Warning*: Your app will expire soon! Use `/sideload` to refresh.' if status['days_remaining'] < 7 else '')}"""
            
            send_telegram_message(chat_id, message)
            
        else:
            # Likely a UDID
            send_telegram_message(chat_id, f"""📱 *Device Status: {identifier}*

⚠️ This feature is coming soon. For now, please check individual apps by bundle ID.

To check a specific app, use:
`/status com.example.myapp`""")
    
    except Exception as e:
        import logging
        logging.error(f"Error in install status handling: {e}")
        send_telegram_message(chat_id, f"❌ *Error*\n\nAn error occurred while checking installation status: {str(e)}")
