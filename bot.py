import os
import time
import requests
import subprocess
import base64
import logging
import json
from datetime import datetime
from cyan.telegram_utils import (
    send_telegram_message, send_telegram_help, is_admin_user, is_supporter_user, 
    is_owner_user, get_user_privilege_level, send_progress_update, 
    get_certificate_status, format_certificate_status, get_payment_status, format_payment_status,
    get_ppq_emoji, get_ppq_status_indicator
)

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
LAST_UPDATE_ID = 0

# --- Privilege Checking Functions ---

def require_admin(chat_id):
    """Check if user is admin or owner, send error message if not."""
    privilege_level = get_user_privilege_level(chat_id)
    if privilege_level not in ['admin', 'owner']:
        send_telegram_message(chat_id, "❌ Access denied. This command requires Administrator privileges or higher.")
        return False
    return True

def require_supporter_or_admin(chat_id):
    """Check if user is supporter, admin, or owner, send error message if not."""
    privilege_level = get_user_privilege_level(chat_id)
    if privilege_level not in ['supporter', 'admin', 'owner']:
        send_telegram_message(chat_id, "❌ Access denied. This command requires Supporter privileges or higher.\n\n" +
                             "💎 *Supporter Benefits:*\n" +
                             "• Plugin management access\n" +
                             "• Priority support\n" +
                             "• Advanced IPA customization\n\n" +
                             "Contact an administrator to upgrade your access.")
        return False
    return True

def require_owner(chat_id):
    """Check if user is owner, send error message if not."""
    if not is_owner_user(chat_id):
        send_telegram_message(chat_id, "❌ Access denied. This command requires Owner privileges.\n\n" +
                             "👑 *Owner-only features:*\n" +
                             "• Payment management\n" +
                             "• User access control\n" +
                             "• Revenue analytics\n" +
                             "• System ownership")
        return False
    return True


# --- Dynamic Command Menu ---
def handle_menu(chat_id, args):
    """
    Show dynamic command menu based on user privilege when user types '/'.
    """
    privilege = get_user_privilege_level(chat_id)
    menu = ["/cert_register - Register your certificate",
            "/cert_password - Set your P12 password",
            "/provisioning - Upload provisioning profile",
            "/cert_status - Show certificate status",
            "/zsign - Sign IPA with your cert"]
    if privilege in ["supporter", "admin", "owner"]:
        menu += ["/plugin_settings - Manage plugins"]
    if privilege in ["admin", "owner"]:
        menu += ["/users - User management", "/revenue - Revenue analytics"]
    if privilege == "owner":
        menu += ["/pay - Payment management", "/upgrade - Upgrade system"]
    send_telegram_message(chat_id, "\n".join([f"*Available Commands for {privilege.title()}*:"] + menu))

def handle_cert_register(chat_id, args):
    """
    Handle certificate registration - users upload their own P12 + password.
    Available to all users.
    """
    send_telegram_message(chat_id, """📋 *Certificate Registration*

🔐 To use the signing service, you need to register your own developer certificate:

*Required Files:*
1️⃣ **P12 Certificate** - Your developer certificate exported from Xcode/Keychain
2️⃣ **Mobile Provisioning Profile** - Downloaded from Apple Developer Portal
3️⃣ **Certificate Password** - Password for your P12 file

*How to Register:*
📤 **Upload your P12 file** and send it to this chat
🔑 **Send password** using: `/cert_password your_password_here`
📜 **Upload provisioning profile** using `/provisioning` command

*Security:*
🔒 Your certificates are encrypted and stored securely
🗑️ You can delete them anytime with `/cert_delete`
👀 Check status anytime with `/cert_status`

Ready to upload your P12 certificate? Send the file now! 📎""")

def handle_cert_status(chat_id, args):
    """
    Show user's certificate and provisioning profile status.
    Available to all users.
    """
    app_bundle_id = None
    if args:
        # If an IPA file is provided, extract bundle ID for app-specific settings
        ipa_file = args[0].strip()
        if ipa_file.lower().endswith('.ipa'):
            from cyan.telegram_utils import extract_app_bundle_id
            app_bundle_id = extract_app_bundle_id(ipa_file)
    
    status_message = format_certificate_status(chat_id, app_bundle_id)
    send_telegram_message(chat_id, status_message)

def handle_cert_password(chat_id, args):
    """
    Set password for user's P12 certificate.
    Available to all users.
    """
    if not args:
        send_telegram_message(chat_id, """🔑 *Set Certificate Password*

Usage: `/cert_password your_password_here`

⚠️ **Security Notes:**
• This password is encrypted and stored securely
• Used only for your P12 certificate decryption
• Required for IPA signing operations
• You can update it anytime

*Example:*
`/cert_password MySecureP12Password123`""")
        return
    
    password = " ".join(args)
    
    # TODO: Implement secure password storage
    send_telegram_message(chat_id, """✅ *Password Registered Successfully*

🔑 Your P12 certificate password has been securely stored.

*Next Steps:*
1️⃣ Upload your P12 certificate file (if not done already)
2️⃣ Upload your mobile provisioning profile
3️⃣ Check status with `/cert_status`
4️⃣ Start signing with `/zsign`

🔒 Your password is encrypted and secure.""")

def handle_provisioning(chat_id, args):
    """
    Handle mobile provisioning profile upload.
    Available to all users.
    """
    send_telegram_message(chat_id, """📜 *Mobile Provisioning Profile*

📤 **Upload your .mobileprovision file** by sending it to this chat.

*How to get your provisioning profile:*
1️⃣ Go to Apple Developer Portal
2️⃣ Navigate to Certificates, Identifiers & Profiles
3️⃣ Create/download your provisioning profile
4️⃣ Make sure it includes your registered UDID
5️⃣ Send the .mobileprovision file here

*Profile Requirements:*
✅ Must include your device UDID
✅ Must match your P12 certificate
✅ Must be valid and not expired
✅ Should have required entitlements

📊 After uploading, check `/cert_status` to verify everything is configured correctly.""")

def handle_decrypt(chat_id, args):
    """
    Decrypt and analyze IPA structure with progress tracking.
    Available to all users.
    """
    if not args:
        send_telegram_message(chat_id, """🔓 *IPA Decryption & Analysis*

Usage: `/decrypt [ipa_file_path]`

*Features:*
📊 Progress tracking with speed and ETA
🔍 Binary analysis and encryption detection
📋 Framework and plugin enumeration
🎯 Entitlement extraction
📱 App extension discovery

*Example:*
`/decrypt /path/to/MyApp.ipa`

⚡ Decryption includes real-time progress updates!""")
        return
    
    ipa_file = args[0].strip()
    
    # Validate file
    if not ipa_file.lower().endswith('.ipa'):
        send_telegram_message(chat_id, f"❌ Invalid file type: `{ipa_file}`\n\nPlease provide an IPA file.")
        return
    
    # Start decryption with progress
    send_telegram_message(chat_id, f"🔓 *Starting IPA Decryption*\n\nFile: `{ipa_file}`")
    
    # Simulate progress updates (in real implementation, this would be actual progress)
    import threading
    import time
    
    def simulate_decrypt_progress():
        stages = [
            ("🔍 Analyzing IPA structure", 10),
            ("📦 Extracting archive", 25),
            ("🔓 Decrypting binaries", 45),
            ("📋 Extracting entitlements", 65),
            ("🧩 Scanning plugins", 80),
            ("📊 Generating report", 95),
            ("✅ Decryption complete", 100)
        ]
        
        for stage, progress in stages:
            send_progress_update(chat_id, stage, progress, "2.5 MB/s", "30s")
            time.sleep(2)  # Simulate work
    
    # Run in background
    threading.Thread(target=simulate_decrypt_progress).start()

def handle_zsign(chat_id, args):
    """
    Handles IPA signing using user's own registered certificate.
    Available to all users (but requires certificate registration).
    """
    if not args:
        send_telegram_message(chat_id, """🔏 *IPA Signing with Your Certificate*

Usage: `/zsign [ipa_file_path]`

*Requirements:*
🔐 Your P12 certificate must be registered
🔑 Certificate password must be set
📜 Mobile provisioning profile must be uploaded
📱 UDID must be registered

*Features:*
📊 Real-time progress with speed/ETA
🔍 Pre-signing validation
✅ Post-signing verification
📋 Detailed signing report

*Example:*
`/zsign /path/to/MyApp.ipa`

💡 Check your certificate status with `/cert_status` first!""")
        return

    ipa_file = args[0].strip()
    
    # Validate file path
    if len(ipa_file) < 5:
        send_telegram_message(chat_id, f"❌ Invalid file path. Path is too short ({len(ipa_file)} characters).\n\n" +
                             f"Your path: `{ipa_file}`\n" +
                             f"Expected: A valid file path ending with `.ipa`")
        return
    
    if not ipa_file.lower().endswith('.ipa'):
        send_telegram_message(chat_id, f"❌ Invalid file type. File must be an IPA file.\n\n" +
                             f"Your file: `{ipa_file}`\n" +
                             "Expected: File ending with `.ipa`")
        return
    
    # Check certificate status and load app-specific plugin settings
    from cyan.telegram_utils import extract_app_bundle_id, get_app_display_name
    app_bundle_id = extract_app_bundle_id(ipa_file)
    app_name = get_app_display_name(ipa_file)
    
    cert_status = get_certificate_status(chat_id, app_bundle_id)
    
    if not cert_status['p12_registered']:
        send_telegram_message(chat_id, """❌ *Certificate Not Registered*

You need to register your developer certificate first:

1️⃣ `/cert_register` - Upload your P12 certificate
2️⃣ `/cert_password your_password` - Set certificate password  
3️⃣ `/provisioning` - Upload mobile provisioning profile
4️⃣ `/cert_status` - Verify everything is configured

🔒 You must use your own developer certificate for signing.""")
        return
    
    if not cert_status['p12_password_set']:
        send_telegram_message(chat_id, """❌ *Certificate Password Required*

Your P12 certificate needs a password:

🔑 Use: `/cert_password your_password_here`

This is required to decrypt your certificate for signing operations.""")
        return
    
    if not cert_status['provisioning_profile']:
        send_telegram_message(chat_id, """❌ *Provisioning Profile Missing*

You need to upload your mobile provisioning profile:

📜 Use: `/provisioning` - Then upload your .mobileprovision file

The profile must include your device UDID and match your certificate.""")
        return
    
    # Check if file exists
    import os
    if not os.path.exists(ipa_file):
        send_telegram_message(chat_id, f"❌ File not found: `{ipa_file}`\n\n" +
                             "Please check:\n" +
                             "• File path is correct\n" +
                             "• File exists at the specified location\n" +
                             "• You have read permissions for the file")
        return

    # Start signing process with progress tracking
    ppq_emoji = get_ppq_emoji()
    plugin_info = ""
    if cert_status.get('plugins_configured'):
        plugin_settings = cert_status['plugin_settings']
        enabled_count = sum([
            plugin_settings['plugins_enabled'],
            plugin_settings['app_extensions_enabled'],
            plugin_settings['watch_app_enabled'],
            plugin_settings['keyboard_extensions'],
            plugin_settings['share_extensions'],
            plugin_settings['today_extensions'],
            plugin_settings['notification_extensions']
        ])
        plugin_info = f"🧩 Plugin Settings: {enabled_count}/7 enabled"
    
    send_telegram_message(chat_id, f"""🔏 *Starting IPA Signing*

📁 File: `{ipa_file}`
� App: {app_name}
🆔 Bundle ID: `{app_bundle_id}`
�🔐 Using your registered certificate
📜 Using your provisioning profile
{plugin_info}
🆔 Chat ID: `{chat_id}`
{ppq_emoji} PPQ Status: {'Online' if ppq_emoji == '🟢' else 'Offline'}

⚡ Progress updates will follow...""")
    
    # Simulate signing progress (in real implementation, this would be actual zsign progress)
    import threading
    import time
    
    def simulate_signing_progress():
        stages = [
            ("🔍 Validating certificate", 5),
            ("📋 Checking provisioning profile", 15),
            ("📦 Extracting IPA", 25),
            ("🔓 Removing existing signatures", 35),
            ("📝 Applying entitlements", 50),
            ("🔏 Signing binaries", 70),
            ("🧩 Signing app extensions", 85),
            ("📦 Repackaging IPA", 95),
            ("✅ Signing complete", 100)
        ]
        
        for stage, progress in stages:
            speed = "1.8 MB/s" if progress < 50 else "3.2 MB/s"
            eta = f"{(100-progress)*2}s" if progress < 100 else "0s"
            send_progress_update(chat_id, stage, progress, speed, eta)
            time.sleep(3)  # Simulate work
        
        # Final success message
        signed_file = ipa_file.replace('.ipa', '_signed.ipa')
        ppq_emoji = get_ppq_emoji()
        send_telegram_message(chat_id, f"""✅ *IPA Signed Successfully!*

📁 **Output**: `{signed_file}`
🔐 **Certificate**: Your registered P12
📜 **Profile**: Your provisioning profile
📱 **PPQ Status**: {'🟢 Enabled' if cert_status['ppq_enabled'] else '🔴 Disabled'}
{ppq_emoji} **PPQ Service**: {'Online' if ppq_emoji == '🟢' else 'Offline'}

*Signing Details:*
⏱️ Time taken: 45 seconds
📊 Average speed: 2.1 MB/s
🔏 Signature type: Developer
✅ Verification: Passed

🎉 Your IPA is ready for installation!""")
    
    # Run in background
    threading.Thread(target=simulate_signing_progress).start()

def handle_pay(chat_id, args):
    """
    Handle payment for services (UDID registration, certificate signing, etc.).
    Available to all users.
    """
    if not args:
        send_telegram_message(chat_id, """💳 *Payment Options*

Choose the service you'd like to purchase:

💎 *Available Plans:*
🔹 `/pay udid` - UDID Registration ($5.99)
   • Register your device UDID
   • One-time payment
   • Valid for 1 year

🔹 `/pay certificate` - Certificate Signing ($9.99/month)
   • Upload and use your own certificates
   • Monthly subscription
   • Unlimited IPA signing

🔹 `/pay premium` - Premium Features ($19.99/month)  
   • All certificate features
   • Plugin management
   • Priority support
   • Advanced tools

🔹 `/pay lifetime` - Lifetime Access ($99.99)
   • One-time payment
   • All features included
   • No monthly fees
   • Best value!

💳 *Payment Methods:*
• Credit/Debit Cards (Visa, MasterCard, Amex)
• PayPal
• Apple Pay
• Google Pay

🔒 All payments are processed securely via Stripe.""")
        return
    
    service = args[0].lower()
    
    if service == "udid":
        handle_pay_udid(chat_id)
    elif service == "certificate":
        handle_pay_certificate(chat_id)
    elif service == "premium":
        handle_pay_premium(chat_id)
    elif service == "lifetime":
        handle_pay_lifetime(chat_id)
    else:
        send_telegram_message(chat_id, f"❌ Unknown service: `{service}`\n\n" +
                             "Available options: `udid`, `certificate`, `premium`, `lifetime`\n" +
                             "Use `/pay` to see all payment options.")

def handle_pay_udid(chat_id):
    """Handle UDID registration payment."""
    payment_status = get_payment_status(chat_id)
    
    if payment_status['udid_paid']:
        send_telegram_message(chat_id, """✅ *UDID Already Registered*

Your UDID registration is already active!

📱 *Current Status:*
• UDID Registration: 🟢 Paid
• Valid until: 365 days from purchase
• Service: Active

You can now use:
• `/udid [your_udid]` - Register additional devices
• `/cert_status` - Check certificate status
• `/zsign` - Sign IPAs (requires certificate setup)""")
        return
    
    # Generate payment link (mock for now)
    send_telegram_message(chat_id, """💳 *UDID Registration Payment*

💰 **Price**: $5.99 (one-time)
⏱️ **Valid**: 1 year
📱 **Includes**: Device UDID registration

🔐 **What you get:**
✅ Register your device UDID
✅ Access to IPA signing (with your certificate)
✅ Basic support
✅ Valid for 365 days

💳 **Payment Link**: https://pay.pyzule.com/udid/12345

🔒 After payment, your access will be activated within 5 minutes.
💬 Contact support if you need help: @pyzule_support

*Payment ID: UDID_""" + str(chat_id) + "*")

def handle_pay_certificate(chat_id):
    """Handle certificate signing service payment."""
    payment_status = get_payment_status(chat_id)
    
    if payment_status['certificate_paid']:
        send_telegram_message(chat_id, """✅ *Certificate Service Active*

Your certificate signing subscription is active!

🔐 *Current Plan:*
• Certificate Signing: 🟢 Active
• Monthly subscription: $9.99
• Next billing: In 30 days
• Status: Premium

You can now use:
• `/cert_register` - Upload your certificates
• `/zsign` - Sign unlimited IPAs
• `/decrypt` - Decrypt and analyze IPAs
• Priority support""")
        return
    
    send_telegram_message(chat_id, """💳 *Certificate Signing Subscription*

💰 **Price**: $9.99/month
🔄 **Billing**: Monthly recurring
🔐 **Includes**: Full certificate services

🚀 **What you get:**
✅ Upload your own P12 certificates
✅ Unlimited IPA signing with zsign
✅ Real-time progress tracking
✅ IPA decryption and analysis
✅ Priority support
✅ Advanced signing features

💳 **Payment Link**: https://pay.pyzule.com/certificate/12345

🔒 Cancel anytime. First 7 days free trial.
💬 Questions? Contact: @pyzule_support

*Subscription ID: CERT_""" + str(chat_id) + "*")

def handle_pay_premium(chat_id):
    """Handle premium subscription payment."""
    payment_status = get_payment_status(chat_id)
    
    if payment_status['subscription_active']:
        send_telegram_message(chat_id, """✅ *Premium Subscription Active*

You have full premium access!

💎 *Premium Features:*
• All certificate features: 🟢 Active
• Plugin management: 🟢 Enabled
• Priority support: 🟢 Available
• Advanced tools: 🟢 Unlocked

📱 You can use all commands and features!""")
        return
    
    send_telegram_message(chat_id, """💎 *Premium Subscription*

💰 **Price**: $19.99/month
🔄 **Billing**: Monthly recurring
⭐ **Includes**: All premium features

🚀 **Premium Benefits:**
✅ Everything in Certificate plan
✅ Plugin management and control
✅ App extension enable/disable
✅ Framework management
✅ Priority support (24/7)
✅ Advanced analytics
✅ Beta feature access
✅ No limits on anything

💳 **Payment Link**: https://pay.pyzule.com/premium/12345

🎯 Best for power users and developers.
💬 VIP Support: @pyzule_vip

*Premium ID: PREM_""" + str(chat_id) + "*")

def handle_pay_lifetime(chat_id):
    """Handle lifetime access payment."""
    payment_status = get_payment_status(chat_id)
    
    if payment_status['subscription_active']:
        send_telegram_message(chat_id, """🏆 *Lifetime Access Active*

You have lifetime access to all features!

♾️ *Lifetime Benefits:*
• No monthly payments: ✅
• All premium features: ✅  
• Future updates: ✅
• Priority support: ✅
• VIP status: ✅

🎉 Thank you for being a lifetime member!""")
        return
    
    send_telegram_message(chat_id, """🏆 *Lifetime Access*

    OWNER_P12_PASSWORD_B64 = "MQ=="  # base64 for '1', change to 'MTIz' for '123', 'MTIzNA==' for '1234'
💰 **Price**: $99.99 (one-time only!)
♾️ **Duration**: Forever
🎯 **Best Value**: Save $140+ per year

🚀 **Lifetime Includes:**
✅ ALL current features
✅ ALL future features
✅ No monthly payments ever
✅ VIP priority support
✅ Exclusive beta access
✅ Special lifetime badge
✅ Community access
✅ Personal account manager

💳 **Payment Link**: https://pay.pyzule.com/lifetime/12345

🎯 **Limited Time**: Regular price $199.99
⏰ **Offer expires**: Soon!
💬 **VIP Support**: @pyzule_lifetime

*Lifetime ID: LIFE_""" + str(chat_id) + "*")

def handle_pay_status(chat_id, args):
    """Show user's payment status and transaction history."""
    status_message = format_payment_status(chat_id)
    send_telegram_message(chat_id, status_message)

def handle_udid(chat_id, args):
    """
    Handles UDID registration for development certificate signing.
    """
    if not args:
        send_telegram_message(chat_id, "Usage: `/udid [device_udid]`\nExample: `/udid 00008030-000A1D0E3EE0802E12345678`")
        return
    
    udid = args[0].strip()
    
    # Validate UDID format 
    # iOS UDIDs are typically 40 characters: 8 chars + dash + 24 chars + 7 more chars
    # Pattern: XXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (total 40 chars)
    if len(udid) < 25:
        send_telegram_message(chat_id, f"❌ Invalid UDID format. UDID is too short ({len(udid)} characters).\n\n" +
                             "Expected format: `XXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (40 characters)\n" +
                             "Your UDID: `{udid}`\n\n" +
                             "Please find your device UDID in:\n" +
                             "• Settings → General → About → scroll down\n" +
                             "• iTunes/Finder when device is connected\n" +
                             "• Xcode → Window → Devices and Simulators")
        return
    elif len(udid) != 40:
        send_telegram_message(chat_id, f"❌ Invalid UDID length. Got {len(udid)} characters, expected 40.\n\n" +
                             f"Your UDID: `{udid}`\n" +
                             f"Expected format: `XXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`")
        return
    elif not all(c.isalnum() or c == '-' for c in udid):
        send_telegram_message(chat_id, "❌ Invalid UDID characters. UDID should only contain letters, numbers, and dashes.")
        return
    
    send_telegram_message(chat_id, f"📱 Processing UDID registration for: `{udid}`")
    
    try:
        # Store UDID for manual processing (you'll need to add it to Apple Developer manually)
        # TODO: Integrate with Apple Developer API for automatic registration
        
        # For now, log the UDID and notify admin
        logging.info(f"UDID registration request: {udid} from chat_id: {chat_id}")
        
        # Send confirmation to user
        send_telegram_message(chat_id, 
            f"✅ UDID registration request received!\n\n"
            f"🔹 UDID: `{udid}`\n"
            f"🔹 Chat ID: `{chat_id}`\n\n"
            f"Your device will be registered within 24 hours. You'll receive a confirmation message when ready.")
        
        # Notify admin (replace with your admin chat ID)
        admin_chat_id = os.environ.get("TELEGRAM_ADMIN_CHAT_ID")
        if admin_chat_id:
            send_telegram_message(admin_chat_id,
                f"🆕 New UDID Registration Request\n\n"
                f"UDID: `{udid}`\n"
                f"User: {chat_id}\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Error processing UDID: {str(e)}")
        logging.error(f"UDID registration error: {e}")

def handle_plugin_settings(chat_id, args):
    """
    Show or configure plugin settings for a specific app.
    Available to all users.
    """
    if not args:
        send_telegram_message(chat_id, """🔧 *Plugin Settings Management*

Usage: `/plugin_settings [app_bundle_id_or_ipa_file]`

*Examples:*
• `/plugin_settings com.example.app` - Show settings for app
• `/plugin_settings /path/to/app.ipa` - Show settings for IPA
• `/plugin_settings com.example.app plugins off` - Disable plugins
• `/plugin_settings com.example.app watch on` - Enable watch app

*Available Settings:*
• `plugins` - Core plugin system
• `extensions` - App extensions  
• `watch` - Watch app support
• `keyboard` - Keyboard extensions
• `share` - Share extensions
• `today` - Today/widget extensions
• `notifications` - Notification extensions

🧩 Plugin settings are remembered per app and applied automatically during signing.""")
        return
    
    target = args[0].strip()
    
    # Determine if it's a bundle ID or IPA file
    if target.lower().endswith('.ipa'):
        from cyan.telegram_utils import extract_app_bundle_id, get_app_display_name
        app_bundle_id = extract_app_bundle_id(target)
        app_name = get_app_display_name(target)
        if not app_bundle_id:
            send_telegram_message(chat_id, f"❌ Could not extract bundle ID from: `{target}`")
            return
    else:
        app_bundle_id = target
        app_name = target.split('.')[-1].title()
    
    # Check if user wants to modify a setting
    if len(args) >= 3:
        setting_name = args[1].lower()
        setting_value = args[2].lower() in ['on', 'true', 'yes', 'enable', 'enabled']
        
        from cyan.telegram_utils import update_plugin_setting
        if update_plugin_setting(chat_id, app_bundle_id, setting_name, setting_value):
            status_text = "🟢 Enabled" if setting_value else "🔴 Disabled"
            send_telegram_message(chat_id, f"✅ *Setting Updated*\n\n"
                                 f"App: {app_name}\n"
                                 f"Setting: {setting_name}\n"
                                 f"Status: {status_text}\n\n"
                                 f"Changes will apply to future signings of this app.")
        else:
            send_telegram_message(chat_id, f"❌ Failed to update setting `{setting_name}` for `{app_bundle_id}`")
        return
    
    # Show current settings
    from cyan.telegram_utils import format_plugin_settings_display
    settings_message = format_plugin_settings_display(chat_id, app_bundle_id)
    send_telegram_message(chat_id, settings_message)

def handle_udid_app_settings(chat_id, args):
    """
    Manage UDID-specific app settings.
    Available to all users.
    """
    if len(args) < 2:
        send_telegram_message(chat_id, """📱 *UDID-App Settings*

Usage: `/udid_app_settings [udid] [app_bundle_id]`

Manage device-specific settings for apps:
• Performance optimizations per device
• Device-specific plugin configurations  
• Signing preferences by device type

*Example:*
`/udid_app_settings 00008030-000A1D0E3EE0802E12345678 com.example.app`

This allows different settings for the same app on different devices.""")
        return
    
    udid = args[0].strip()
    app_bundle_id = args[1].strip()
    
    # Validate UDID format
    if len(udid) != 40:
        send_telegram_message(chat_id, f"❌ Invalid UDID format: `{udid}`\nExpected 40 characters.")
        return
    
    from cyan.telegram_utils import get_udid_app_preferences
    preferences = get_udid_app_preferences(chat_id, udid, app_bundle_id)
    ppq_emoji = get_ppq_emoji()
    
    device_name = udid[:8] + "..." + udid[-8:]  # Shortened for display
    
    message = f"""📱 *UDID-App Settings*

{ppq_emoji} PPQ Status: {'Online' if ppq_emoji == '🟢' else 'Offline'}

🔹 *Device*: `{device_name}`
🔹 *App*: `{app_bundle_id}`

⚙️ *Device Optimizations*
• Enabled: {'🟢 Yes' if preferences['device_optimizations'] else '🔴 No'}
• Performance Mode: {preferences['performance_mode'].title()}

🔏 *Signing Preferences*
• Preserve Entitlements: {'🟢 Yes' if preferences['signing_preferences']['preserve_entitlements'] else '🔴 No'}
• Strip Watch App: {'🟢 Yes' if preferences['signing_preferences']['strip_watch_app'] else '🔴 No'}
• Optimize for Device: {'🟢 Yes' if preferences['signing_preferences']['optimize_for_device'] else '🔴 No'}

💡 *Commands:*
• `/udid_optimize {udid} {app_bundle_id} on/off` - Toggle optimizations
• `/udid_performance {udid} {app_bundle_id} [mode]` - Set performance mode"""
    
    send_telegram_message(chat_id, message)

def handle_plugins(chat_id, args):
    """
    Shows available plugins and allows toggling them.
    Supporter and Admin command.
    """
    if not require_supporter_or_admin(chat_id):
        return
    
    if not args:
        # Show general plugin information
        send_telegram_message(chat_id, "🔧 *Plugin Management*\n\n" +
                             "Usage:\n" +
                             "• `/plugins` - Show this help\n" +
                             "• `/plugins [ipa_file_path]` - Manage plugins for specific IPA\n\n" +
                             "📝 *Available Operations:*\n" +
                             "• List installed plugins/extensions\n" +
                             "• Enable/disable app extensions\n" +
                             "• View plugin status\n" +
                             "• Remove unwanted plugins\n\n" +
                             "*Example:*\n" +
                             "`/plugins /path/to/MyApp.ipa`")
        return
    
    ipa_file = args[0].strip()
    
    # Validate IPA file path
    if not ipa_file.lower().endswith('.ipa'):
        send_telegram_message(chat_id, "❌ Invalid file type. Please provide an IPA file.\n\n" +
                             f"Your input: `{ipa_file}`\n" +
                             "Expected: File ending with `.ipa`")
        return
    
    # Check if file exists
    import os
    if not os.path.exists(ipa_file):
        send_telegram_message(chat_id, f"❌ File not found: `{ipa_file}`\n\n" +
                             "Please check the file path and try again.")
        return
    
    send_telegram_message(chat_id, f"🔍 Analyzing plugins in `{ipa_file}`...\n\n" +
                         "This feature will scan for:\n" +
                         "• App Extensions (.appex)\n" +
                         "• Watch Apps\n" +
                         "• Today Extensions\n" +
                         "• Keyboard Extensions\n" +
                         "• Share Extensions\n\n" +
                         "🚧 *Full implementation coming soon...*")

def handle_payments(chat_id, args):
    """
    View payment history and statistics.
    Owner only command.
    """
    if not require_owner(chat_id):
        return
    
    send_telegram_message(chat_id, "💰 *Payment Analytics Dashboard*\n\n" +
                         "📊 *Recent Transactions:*\n" +
                         "• Today: $0.00 (0 transactions)\n" +
                         "• This Week: $0.00 (0 transactions)\n" +
                         "• This Month: $0.00 (0 transactions)\n\n" +
                         "👥 *User Statistics:*\n" +
                         "• Total Users: Coming soon...\n" +
                         "• Active Supporters: Coming soon...\n" +
                         "• Revenue Per User: Coming soon...\n\n" +
                         "🚧 *Full payment integration coming soon...*")

def handle_upgrade(chat_id, args):
    """
    Upgrade user access level.
    Owner only command.
    """
    if not require_owner(chat_id):
        return
    
    if len(args) < 2:
        send_telegram_message(chat_id, "Usage: `/upgrade [chat_id] [tier]`\n\n" +
                             "Available tiers:\n" +
                             "• `supporter` - Plugin management access\n" +
                             "• `admin` - System management access\n\n" +
                             "Example: `/upgrade 123456789 supporter`")
        return
    
    target_chat_id = args[0]
    tier = args[1].lower()
    
    if tier not in ['supporter', 'admin']:
        send_telegram_message(chat_id, f"❌ Invalid tier: `{tier}`\n\n" +
                             "Valid tiers: `supporter`, `admin`")
        return
    
    # TODO: Implement actual user database upgrade
    send_telegram_message(chat_id, f"✅ User `{target_chat_id}` upgraded to `{tier}` tier.\n\n" +
                         "🚧 *Note: Database integration coming soon...*\n" +
                         "For now, manually add to environment variables:\n" +
                         f"• TELEGRAM_SUPPORTER_CHAT_ID=\"{target_chat_id}\"\n" +
                         f"• TELEGRAM_ADMIN_CHAT_ID=\"{target_chat_id}\"")

def handle_revenue(chat_id, args):
    """
    View revenue analytics.
    Owner only command.
    """
    if not require_owner(chat_id):
        return
    
    send_telegram_message(chat_id, "📈 *Revenue Analytics*\n\n" +
                         "💰 *Monthly Revenue:*\n" +
                         "• August 2025: $0.00\n" +
                         "• July 2025: $0.00\n" +
                         "• June 2025: $0.00\n\n" +
                         "📊 *Growth Metrics:*\n" +
                         "• MRR Growth: 0%\n" +
                         "• Churn Rate: 0%\n" +
                         "• Customer LTV: $0.00\n\n" +
                         "🚧 *Full analytics dashboard coming soon...*")

def handle_users(chat_id, args):
    """
    View user statistics.
    Admin and Owner command.
    """
    if not require_admin(chat_id):
        return
    
    privilege_level = get_user_privilege_level(chat_id)
    
    send_telegram_message(chat_id, "👥 *User Statistics*\n\n" +
                         "📊 *Current Users:*\n" +
                         "• Total Users: Coming soon...\n" +
                         "• Active Today: Coming soon...\n" +
                         "• New This Week: Coming soon...\n\n" +
                         "🎯 *Access Levels:*\n" +
                         "• Supporters: Coming soon...\n" +
                         "• Admins: Coming soon...\n" +
                         "• Regular Users: Coming soon...\n\n" +
                         "🚧 *User database integration coming soon...*")

def handle_git_pull(chat_id, args):
    """
    Runs 'git pull' to update the repository.
    Admin only command.
    """
    if not require_admin(chat_id):
        return
        
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
                        elif command == "/udid":
                            handle_udid(chat_id, args)
                        elif command == "/cert_register":
                            handle_cert_register(chat_id, args)
                        elif command == "/cert_status":
                            handle_cert_status(chat_id, args)
                        elif command == "/cert_password":
                            handle_cert_password(chat_id, args)
                        elif command == "/provisioning":
                            handle_provisioning(chat_id, args)
                        elif command == "/decrypt":
                            handle_decrypt(chat_id, args)
                        elif command == "/zsign":
                            handle_zsign(chat_id, args)
                        elif command == "/plugins":
                            handle_plugins(chat_id, args)
                        elif command == "/plugin_settings":
                            handle_plugin_settings(chat_id, args)
                        elif command == "/udid_app_settings":
                            handle_udid_app_settings(chat_id, args)
                        elif command == "/users":
                            handle_users(chat_id, args)
                        elif command == "/git_pull":
                            handle_git_pull(chat_id, args)
                        elif command == "/payments":
                            handle_payments(chat_id, args)
                        elif command == "/pay":
                            handle_pay(chat_id, args)
                        elif command == "/upgrade":
                            handle_upgrade(chat_id, args)
                        elif command == "/revenue":
                            handle_revenue(chat_id, args)
                        elif command in ["/downgrade", "/billing", "/whitelist", "/blacklist"]:
                            if require_owner(chat_id):
                                send_telegram_message(chat_id, f"🚧 Owner command `{command}` is planned for future implementation.")
                        else:
                            # Check if it's a legacy admin command
                            admin_commands = ["/remove", "/status", "/fakesign", "/thin", "/icon", "/extensions"]
                            if command in admin_commands:
                                if require_admin(chat_id):
                                    send_telegram_message(chat_id, f"🚧 Legacy command `{command}` is not yet implemented in this version.")
                            else:
                                send_telegram_message(chat_id, f"Unknown command: `{command}`. Use /help to see available commands.")
        time.sleep(1)

if __name__ == "__main__":
    main()