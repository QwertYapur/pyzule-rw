"""
Sideloading utilities for Telegram bot integration
Provides helpers for generating installation links, QR codes, and AltStore integration
"""
import os
import logging
import requests
from io import BytesIO
# PIL (Pillow) is not required directly here because qrcode.make_image() returns an image object;
# avoid importing PIL.Image directly to prevent static analysis errors in environments
# where Pillow is not installed. If you need to perform Pillow-specific operations,
# import PIL.Image inside the function that requires it.
from typing import Optional, Dict, Any, Tuple

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Try to import the optional qrcode library; if unavailable, fall back to a remote QR service.
try:
    # dynamic import avoids static-analysis false-positives when qrcode isn't installed
    import importlib
    qrcode = importlib.import_module('qrcode')
    # Access constants via attribute with a safe fallback
    from typing import Any
    qrcode_constants: Any = getattr(qrcode, 'constants', None)
    if qrcode_constants is None:
        class _QrConstants:
            # qrcode.constants.ERROR_CORRECT_H is typically 3; provide a fallback so attribute access is safe
            ERROR_CORRECT_H = 3
        qrcode_constants = _QrConstants
    _HAS_QRCODE = True
except Exception:
    qrcode = None
    class _FallbackQrConstants:
        # qrcode.constants.ERROR_CORRECT_H is typically 3; provide a fallback so attribute access is safe
        ERROR_CORRECT_H = 3
    qrcode_constants = _FallbackQrConstants
    _HAS_QRCODE = False
    logging.warning("qrcode module not available, falling back to remote QR generation via api.qrserver.com")

# --- QR Code Generation ---

def generate_qr_code(url: str, size: int = 10) -> BytesIO:
    """Generate QR code for the given URL and return as BytesIO.

    If the local `qrcode` package is available, use it to create the image.
    Otherwise, request a PNG from a public QR code API (api.qrserver.com).
    """
    # Ensure the module is present and provides QRCode before calling into it.
    if _HAS_QRCODE and qrcode is not None and hasattr(qrcode, "QRCode"):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode_constants.ERROR_CORRECT_H,
            box_size=size,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to BytesIO for easy transmission
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, 'PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr

    # Fallback: use a remote QR generation service to avoid requiring the qrcode package.
    api_url = "https://api.qrserver.com/v1/create-qr-code/"
    # approximate size: each qrcode.box_size ~= 25 pixels; api accepts WxH strings
    params = {
        "data": url,
        "size": f"{max(100, size * 25)}x{max(100, size * 25)}",
        "format": "png",
    }
    resp = requests.get(api_url, params=params, timeout=10)
    resp.raise_for_status()
    return BytesIO(resp.content)

# --- Installation URL Generation ---

def generate_install_url(file_url: str, app_name: str) -> str:
    """Generate direct installation URL for iOS devices."""
    # For direct installation, we use the itms-services protocol
    plist_url = f"https://sideloadservice.example.com/generate_plist?app_url={file_url}&app_name={app_name}"
    install_url = f"itms-services://?action=download-manifest&url={plist_url}"
    return install_url

def generate_altstore_url(file_url: str) -> str:
    """Generate AltStore compatible URL."""
    return f"altstore://install?url={file_url}"

# --- Installation Instructions ---

def get_sideloading_instructions(method: str = 'altstore') -> str:
    """Get formatted instructions for sideloading based on the chosen method."""
    instructions = {
        'altstore': """📱 *AltStore Installation Instructions*

1️⃣ Make sure [AltStore](https://altstore.io) is installed on your device
2️⃣ Click the AltStore link in this message
3️⃣ AltStore will open and begin installing the app
4️⃣ Enter your Apple ID if prompted

⚠️ *Requirements*:
• AltStore must be installed and active
• Your computer with AltServer must be on the same WiFi network
• Your Apple ID must be set up in AltServer""",

        'sideloadly': """📱 *Sideloadly Installation Instructions*

1️⃣ Download the IPA from the link above
2️⃣ Connect your iPhone to your computer
3️⃣ Open [Sideloadly](https://sideloadly.io) on your computer
4️⃣ Drag and drop the IPA into Sideloadly
5️⃣ Enter your Apple ID and password
6️⃣ Click Start to install

⚠️ *Requirements*:
• Computer with macOS or Windows
• Latest iTunes installed (Windows)
• Apple ID (developer account not required)""",

        'direct': """📱 *Direct Installation Instructions*

1️⃣ Click the "Install Directly" button below
2️⃣ When prompted, select "Install"
3️⃣ Wait for installation to complete
4️⃣ Trust the developer in Settings > General > VPN & Device Management

⚠️ *Notes*:
• This method requires the app to be signed with a valid certificate
• If you see "Unable to Install App", you may need to try a different method"""
    }
    
    return instructions.get(method.lower(), instructions['altstore'])

# --- Sideloading Service Integration ---

def check_app_status(bundle_id: str, udid: Optional[str] = None) -> Dict[str, Any]:
    """Check installation status of an app for a device."""
    # This would typically call an API or service
    # Mock implementation
    return {
        'installed': True,
        'version': '1.0.0',
        'expiry': '2025-09-23',
        'days_remaining': 30
    }

def get_installation_services() -> Dict[str, Dict[str, Any]]:
    """Get available sideloading services and their status."""
    return {
        'altstore': {
            'name': 'AltStore',
            'status': 'available',
            'requires_computer': True,
            'free_tier_available': True
        },
        'sideloadly': {
            'name': 'Sideloadly',
            'status': 'available',
            'requires_computer': True,
            'free_tier_available': True
        },
        'direct': {
            'name': 'Direct Install',
            'status': 'available',
            'requires_certificate': True,
            'free_tier_available': False
        }
    }

# --- File Handling ---

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from an IPA file."""
    # Mock implementation - in real use this would analyze the IPA
    file_name = os.path.basename(file_path)
    return {
        'file_name': file_name,
        'app_name': file_name.replace('.ipa', ''),
        'bundle_id': f'com.example.{file_name.replace(".ipa", "").lower()}',
        'version': '1.0.0',
        'size_mb': os.path.getsize(file_path) / (1024 * 1024)
    }

# --- Main Functions ---

def create_sideload_message(file_url: str, file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Create a formatted message with sideloading options and inline keyboard."""
    metadata = get_file_metadata(file_path)
    
    # Create installation links
    altstore_url = generate_altstore_url(file_url)
    direct_url = generate_install_url(file_url, metadata['app_name'])
    
    message = f"""🚀 *App Ready for Sideloading*

📱 *App*: {metadata['app_name']}
📦 *Size*: {metadata['size_mb']:.2f} MB
🆔 *Bundle ID*: {metadata['bundle_id']}
🔢 *Version*: {metadata['version']}

📥 *Download Link*:
{file_url}

Choose a sideloading method below:"""

    keyboard = {
        'inline_keyboard': [
            [
                {'text': '📲 Install with AltStore', 'url': altstore_url}
            ],
            [
                {'text': '💻 Sideloadly Instructions', 'callback_data': 'sideload_instructions_sideloadly'}
            ],
            [
                {'text': '📱 Direct Installation', 'url': direct_url}
            ],
            [
                {'text': '📋 Show All Instructions', 'callback_data': 'sideload_all_instructions'}
            ],
            [
                {'text': '🔍 Check Installation Status', 'callback_data': f'check_install_status_{metadata["bundle_id"]}'}
            ]
        ]
    }
    
    return message, keyboard

def handle_sideload_callback(callback_data: str, chat_id: str, file_url: Optional[str] = None) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Handle callback queries for sideloading options."""
    if callback_data.startswith('sideload_instructions_'):
        method = callback_data.replace('sideload_instructions_', '')
        return get_sideloading_instructions(method), None
    
    elif callback_data == 'sideload_all_instructions':
        message = """📱 *All Sideloading Methods*

Choose the method that works best for you:

*1. AltStore (Recommended)*
{0}

*2. Sideloadly*
{1}

*3. Direct Installation*
{2}

If you encounter issues, try a different method or contact support.""".format(
            get_sideloading_instructions('altstore'),
            get_sideloading_instructions('sideloadly'),
            get_sideloading_instructions('direct')
        )
        return message, None
    
    elif callback_data.startswith('check_install_status_'):
        bundle_id = callback_data.replace('check_install_status_', '')
        status = check_app_status(bundle_id)
        
        message = f"""📊 *App Installation Status*

🆔 *Bundle ID*: {bundle_id}
✅ *Installed*: {'Yes' if status['installed'] else 'No'}
🔢 *Version*: {status['version']}
⏰ *Expires*: {status['expiry']}
📅 *Days Remaining*: {status['days_remaining']}

{('⚠️ *Warning*: Your app will expire soon! Consider refreshing the installation.' if status['days_remaining'] < 7 else '')}"""
        
        return message, None
    
    return "Unknown action", None

# --- Example Usage ---
if __name__ == "__main__":
    # This is for testing the module directly
    test_url = "https://example.com/test.ipa"
    test_path = "test.ipa"
    
    message, keyboard = create_sideload_message(test_url, test_path)
    print(message)
    print(keyboard)
    
    instructions = get_sideloading_instructions('altstore')
    print(instructions)
    
    qr = generate_qr_code(test_url)
    # In a real scenario, you would send this QR code image to the user
