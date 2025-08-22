import os
import sys
import shutil
import argparse
import subprocess
import plistlib
import json
import getpass
import tempfile
from datetime import datetime

# --- Globals ---
CYAN_DIR = "cyan"
RESOURCES_DIR = os.path.join(CYAN_DIR, "resources")
CONFIG_FILE = "signing_config.json"
# ANSI colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
CHECKMARK = u'\u2713'
CROSS = u'\u2717'

# --- Helper Functions ---

def load_config():
    """Loads signing configuration from the JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"{RED}{CROSS} Error: Configuration file '{CONFIG_FILE}' not found.{RESET}")
        print(f"{YELLOW}Please copy 'signing_config.json.example' to '{CONFIG_FILE}' and fill in your paths.{RESET}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def parse_profile(profile_path):
    """Parses a .mobileprovision file and returns its data and Team ID."""
    try:
        command = ['security', 'cms', '-D', '-i', profile_path]
        plist_xml = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        profile_data = plistlib.loads(plist_xml.encode('utf-8'))
        team_id = profile_data.get('ApplicationIdentifierPrefix', [None])[0]
        return profile_data, team_id
    except (subprocess.CalledProcessError, FileNotFoundError, KeyError, IndexError):
        return None, None

def check_profile_validity(profile_data):
    """Checks the expiration date from parsed profile data."""
    if not profile_data:
        return False
    try:
        exp_date = profile_data['ExpirationDate']
        if exp_date > datetime.now(exp_date.tzinfo):
            print(f"{GREEN}{CHECKMARK} Provisioning Profile is valid. Expires: {exp_date.strftime('%Y-%m-%d')}{RESET}")
            return True
        else:
            print(f"{RED}{CROSS} Provisioning Profile has expired on {exp_date.strftime('%Y-%m-%d')}{RESET}")
            return False
    except KeyError:
        return False

def generate_entitlements(team_id, config):
    """Generates a temporary entitlements file with the correct Team ID."""
    entitlements_dict = {
        'get-task-allow': True,
        'com.apple.security.application-groups': [config['app_group_identifier']],
        'keychain-access-groups': [f"{team_id}.{config['keychain_access_group_base']}"]
    }
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".plist")
    with os.fdopen(fd, 'wb') as fp:
        plistlib.dump(entitlements_dict, fp)
    print(f"{GREEN}Generated temporary entitlements for Team ID: {team_id}{RESET}")
    return temp_path

# --- Main Conversion Logic ---

def convert_artifact_to_cyan(artifact_path, config, p12_password):
    """
    Converts and signs a .dylib or .deb file into a cyan Python module.
    """
    # --- 1. Get Team ID and Generate Entitlements ---
    profile_data, team_id = parse_profile(config['profile_path'])
    if not team_id:
        print(f"{RED}{CROSS} Could not extract Team ID from provisioning profile.{RESET}")
        sys.exit(1)
    
    temp_entitlements_path = generate_entitlements(team_id, config)

    # --- 2. Validation ---
    if not shutil.which('zsign'):
        print(f"{RED}{CROSS} Error: 'zsign' command not found.{RESET}", file=sys.stderr)
        sys.exit(1)

    base_name = os.path.basename(artifact_path)
    module_name, extension = os.path.splitext(base_name)

    # --- 3. Setup Directories ---
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    new_artifact_path = os.path.join(RESOURCES_DIR, base_name)
    shutil.copy(artifact_path, new_artifact_path)
    print(f"{YELLOW}Copied artifact to '{new_artifact_path}'{RESET}")

    # --- 4. Sign with zsign ---
    print(f"{YELLOW}Signing the artifact with zsign...{RESET}")
    zsign_command = [
        'zsign', '-k', config['p12_key_path'], '-m', config['profile_path'], 
        '-c', config['cert_path'], '-p', p12_password, '-f', 
        '-e', temp_entitlements_path, new_artifact_path
    ]
    try:
        subprocess.run(zsign_command, check=True, capture_output=True, text=True)
        print(f"{GREEN}Successfully signed '{base_name}' with zsign.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}{CROSS} Error: zsign failed.{RESET}", file=sys.stderr)
        print(f"zsign error:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    finally:
        # --- 5. Clean up temporary file ---
        os.remove(temp_entitlements_path)

    # --- 6. Create Python Module ---
    cyan_module_path = os.path.join(CYAN_DIR, module_name + '.py')
    # (Boilerplate for the generated module remains the same)
    boilerplate = f"""#!/usr/bin/env python3
#
# Cyan module for managing the '{base_name}' artifact.
#

import os
import subprocess
import sys
from datetime import datetime

# Path to the artifact within the project structure
ARTIFACT_PATH = os.path.join(os.path.dirname(__file__), 'resources', '{base_name}')

# ANSI colors for terminal output
GREEN = '\\033[92m'
RED = '\\033[91m'
RESET = '\\033[0m'
CHECKMARK = u'\\u2713'
CROSS = u'\\u2717'

def check_signature():
    \"\"\"Checks the signature status of the artifact using zsign.\"\"\"
    if not shutil.which('zsign'):
        print(f"{{RED}}{{CROSS}} Error: 'zsign' not found.{{RESET}}", file=sys.stderr)
        return

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Checking signature at {{time_str}}...")

    try:
        subprocess.run(['zsign', '-v', ARTIFACT_PATH], check=True, capture_output=True, text=True)
        print(f"{{GREEN}}{{CHECKMARK}} Signature is valid.{{RESET}}")
    except subprocess.CalledProcessError:
        print(f"{{RED}}{{CROSS}} Signature is INVALID or EXPIRED.{{RESET}}")

def main():
    print(f"--- Status for {{os.path.basename(ARTIFACT_PATH)}} ---")
    if not os.path.exists(ARTIFACT_PATH):
        print(f"{{RED}}{{CROSS}} Artifact file not found.{{RESET}}")
        return
    check_signature()

if __name__ == "__main__":
    import shutil
    main()
"""
    with open(cyan_module_path, 'w') as f:
        f.write(boilerplate)
    print(f"{GREEN}Successfully created cyan module: '{cyan_module_path}'{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert and sign a dylib/deb into a cyan module using zsign.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("inject", metavar="inject", help="Path to the input Inject file (.dylib or .deb).")
    args = parser.parse_args()

    # --- Load Config and Run Checks ---
    config = load_config()
    print("--- Performing Startup Certificate Checks ---")
    profile_data, _ = parse_profile(config['profile_path'])
    profile_ok = check_profile_validity(profile_data)
    print("-------------------------------------------")

    if not profile_ok:
        print(f"{RED}Provisioning profile is invalid. Please check your files.{RESET}")
        sys.exit(1)

    # --- Get Password Securely ---
    try:
        password = getpass.getpass(prompt='Enter password for .p12 key: ')
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        sys.exit(1)

    # --- Proceed with conversion ---
    convert_artifact_to_cyan(
        args.inject,
        config,
        password
    )