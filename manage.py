#!/usr/bin/env python3
"""
Pyzule-RW System Management Utility
Enhanced with PPQ integration and plugin management
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def check_ppq_status():
    """Check PPQ service status."""
    try:
        from cyan.telegram_utils import get_ppq_status_indicator
        status = get_ppq_status_indicator()
        print(f"PPQ Status: {status}")
        return "🟢" in status
    except ImportError:
        print("PPQ Status: 🔴 Not available (telegram_utils not found)")
        return False

def validate_certificates():
    """Run certificate validation."""
    try:
        result = subprocess.run([
            sys.executable, 'p12check.py', '--report'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print("Certificate Validation Report:")
        print("=" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Certificate validation failed: {e}")
        return False

def check_configuration():
    """Check system configuration."""
    config_files = [
        'signing_config.json',
        'dev.entitlements',
        'bot.py',
        'cyan/telegram_utils.py'
    ]
    
    print("Configuration Check:")
    print("=" * 50)
    
    all_good = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} - Missing")
            all_good = False
    
    # Check environment variables
    env_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_ADMIN_CHAT_ID',
        'GOOGLE_DRIVE_FOLDER_ID'
    ]
    
    print("\nEnvironment Variables:")
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - Not set")
            all_good = False
    
    return all_good

def start_bot():
    """Start the Telegram bot."""
    print("Starting Pyzule-RW Telegram Bot...")
    print("=" * 50)
    
    try:
        # Run the bot
        subprocess.run([sys.executable, 'bot.py'], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

def show_status():
    """Show comprehensive system status."""
    print("🔐 Pyzule-RW System Status")
    print("=" * 50)
    
    # PPQ Status
    ppq_online = check_ppq_status()
    
    # Configuration
    print("\nConfiguration:")
    config_ok = check_configuration()
    
    # Certificates
    print("\nCertificates:")
    cert_ok = validate_certificates()
    
    # Overall status
    print("\nOverall Status:")
    if ppq_online and config_ok and cert_ok:
        print("🟢 System Ready")
        return True
    else:
        print("🔴 System Issues Detected")
        return False

def run_plugin_test(app_name=None):
    """Test plugin functionality."""
    print("🧩 Plugin System Test")
    print("=" * 50)
    
    try:
        from cyan.telegram_utils import (
            get_app_plugin_settings,
            save_app_plugin_settings,
            get_ppq_status_indicator
        )
        
        test_app = app_name or "com.apple.Preferences"
        
        # Test plugin settings
        print(f"Testing plugin settings for: {test_app}")
        
        # Save test settings
        test_settings = {
            'frameworks': ['Cephei.framework', 'CepheiPrefs.framework'],
            'custom_bundle_id': f'com.QwertYapur.{test_app.split(".")[-1]}Tweaked',
            'ppq_status': get_ppq_status_indicator()
        }
        
        save_app_plugin_settings(app_name=test_app, settings=test_settings)
        print("✅ Settings saved")
        
        # Retrieve settings
        retrieved = get_app_plugin_settings(test_app)
        print(f"✅ Settings retrieved: {retrieved}")
        
        # Verify PPQ integration
        if 'ppq_status' in retrieved:
            print(f"✅ PPQ Integration: {retrieved['ppq_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Plugin test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Pyzule-RW System Management')
    parser.add_argument('command', choices=[
        'status', 'start', 'check', 'certs', 'ppq', 'plugin-test'
    ], help='Command to run')
    parser.add_argument('--app', help='App name for plugin test')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'start':
        if show_status():
            start_bot()
        else:
            print("❌ System not ready. Fix issues first.")
            sys.exit(1)
    elif args.command == 'check':
        check_configuration()
    elif args.command == 'certs':
        validate_certificates()
    elif args.command == 'ppq':
        check_ppq_status()
    elif args.command == 'plugin-test':
        run_plugin_test(args.app)

if __name__ == '__main__':
    main()
