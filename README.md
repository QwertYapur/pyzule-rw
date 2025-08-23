# 📅 **Project Progress Checklist** (24 August 2025, 19:00)

## 🚀 Major Changes

### ✅ Completed

- [x] 🟢 UDID registration support (🍏🔑): Users can register their device UDID directly through the bot for signing and installation. The bot automates the process and notifies you when your device is ready.
- [x] 🟢 zsign integration (🔏🤖): Fast, dependency-free IPA signing using zsign. The bot uses zsign to sign your IPA with your certificate and provisioning profile, supporting both manual and automated flows.
- [x] 🟢 Sideloading-friendly enhancements: QR code installation links, AltStore compatibility, and direct installation instructions.

- [x] 🟢 Dynamic Telegram bot menu based on user privilege (👑 Owner, 🛡️ Admin, 💸 Supporter, 🧑 User)
- [x] 🟢 User-specific certificate registration and password management 🔐
- [x] 🟢 Owner/admin certificate/password hidden and obfuscated (base64) 🕵️‍♂️
- [x] 🟢 Payment system and multi-tier access (User/Non-Paid 🧑, Premium 💎, Exclusive 👑)
- [x] 🟢 Plugin/App Extension management per app, with persistent settings 🧩
- [x] 🟢 PPQ (Personal Profile Query) status indicators (🟢/🔴) in menus and signing flows 📊
- [x] 🟢 Progress bars and real-time status for decryption/signing (with speed, ETA, and emoji) ⏱️📈
- [x] 🟢 Enhanced error handling and user feedback for all bot commands ⚠️
- [x] 🟢 Modular, extensible architecture for future features 🏗️

### 📝 Minor/Planned

### ⏳ In Progress / TODO

- [ ] 🔄 Integrate Apple Developer API for automatic UDID registration 🍏
- [ ] 🔄 Implement full plugin scanning and toggling in /plugins 🧩
- [ ] 🔄 Add user database and persistent payment tracking for User, Premium, and Exclusive tiers 💳
- [ ] 🔄 Expand analytics and revenue dashboard for owners 📊
- [ ] 🔄 Add more advanced signing and patching options 🛠️
- [ ] 🔄 Continue to improve documentation and onboarding 📚
- [x] 🟢 Improved error handling in Telegram notifications
- [x] 🟢 Fixed chat_id hardcoding in AppBundle class
- [x] 🟢 Code refactoring for better environment variable usage

## 🧬 pyzule-rw / cyan

A modern rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) by tjn, focused on reliability and advanced IPA customization. 🍏📦

Contact: [moinmedong@protonmail.com](mailto:moinmedong@protonmail.com) 📧

---

## 🤡 Welcome to the asdfzxcvbn & YGB Comedy Coding Hour

This is a rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) that doesn't (completely) suck, but if it does, just blame asdfzxcvbn. YGB tried to help, but got distracted by memes and coffee. ☕️😂

> "Why did asdfzxcvbn cross the codebase? To get to the other bug!"
> "YGB tried to optimize the script, but ended up optimizing his snack schedule instead."

Wouldn't a Go rewrite be really cool? Or Rust? 🦀 Every time asdfzxcvbn adds a feature, Python cries a little 🐍😭. YGB says: "If it breaks, just add more print statements!"

---

## 📈 Project Progress (August 2025)

### 🤝 Recent Collaboration & Major Changes

- Telegram bot now supports dynamic privilege-based menus (👑 Owner, 🛡️ Admin, 💸 Supporter, 🧑 User)
- Users must register their own P12 certificate and provisioning profile for signing 🔐
- Owner/admin credentials are hidden and obfuscated (never leaked) 🕵️‍♂️
- Payment system and multi-tier access (User/Non-Paid 🧑, Premium 💎, Exclusive 👑)
- Plugin/App Extension management per app, with persistent settings 🧩
- PPQ (Personal Profile Query) status indicators (🟢/🔴) in menus and signing flows 📊
- Progress bars and real-time status for decryption/signing (with speed, ETA, and emoji) ⏱️📈
- Enhanced error handling and user feedback for all bot commands ⚠️
- All major code and documentation lint issues fixed 🧹
- Modular, extensible architecture for future features 🏗️

### 🧭 What To Do Next

- Integrate Apple Developer API for automatic UDID registration 🍏
- Implement full plugin scanning and toggling in /plugins 🧩
- Add user database and persistent payment tracking 💳
- Expand analytics and revenue dashboard for owners 📊
- Add more advanced signing and patching options 🛠️
- Continue to improve documentation and onboarding 📚

---

## ✨ features (now with 20% more asdfzxcvbn, 80% more YGB)

You can open an issue to request a feature 😁!! Or just @asdfzxcvb and YGB in the issues and watch them argue about tabs vs spaces. 🗨️
Also see my [recommended flags](https://github.com/asdfzxcvbn/pyzule-rw/wiki/recommended-flags) 🚩

- generate and use shareable .cyan files to configure IPAs! 📄
- inject dylib, framework, bundle, and appex files/folders 🧩
- automatically fix dependencies on Cephei* and other common frameworks 🛠️
- copy any unknown file/folder types to app root 📦
- change app name, version, bundle id, and minimum os version 🏷️
- remove UISupportedDevices 🗑️
- remove watch app ⌚️
- change the app icon 🖼️
- fakesign the output ipa/tipa/app 📝
- merge a plist into the app's existing Info.plist 🗂️
- add custom entitlements to the main executable 🛡️
- thin all binaries to arm64, it can LARGELY reduce app size sometimes! 🦴
- remove all app extensions (or just encrypted ones!) 🚫
- Telegram bot for remote app signing and management 🤖
- QR code installation links for easy sideloading 📱
- AltStore and other sideloading tool integration 🔄

## 🛠️ install instructions (asdfzxcvb-proof, YGB-tested)

cyan supports **🐧 linux, 🍏 macOS, 🪟 WSL!** All either x86_64 or arm64/aarch64!!
Tested by YGB, broken by asdfzxcvb, fixed by the community. 🤣

First, ensure you have [ar](https://command-not-found.com/ar) and [tar](https://command-not-found.com/tar) installed. 🛠️

The `zip` and `unzip` commands are *optional* dependencies, they may [fix issues when extracting certain IPAs with chinese characters](https://github.com/asdfzxcvbn/pyzule-rw/wiki/file-does-not-exist-(executable)-%3F), etc 🈚️

Also obviously install python, version 3.9 or greater is required 🐍 (asdfzxcvb once tried 2.7 and summoned a demon 👹)

### 📱 Sideloading Instructions / Telegram Bot Setup

1. Install cyan: `pip install --force-reinstall https://github.com/asdfzxcvbn/pyzule-rw/archive/main.zip` 🚀
2. Configure your Telegram bot:

   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export TELEGRAM_ADMIN_CHAT_ID="your_admin_chat_id"
   export GOOGLE_SERVICE_ACCOUNT_FILE="path/to/service_account.json"
   export GOOGLE_DRIVE_FOLDER_ID="your_drive_folder_id"
   ```

3. Run the bot: `python bot.py` 🤖
4. Send `/start` to your bot to begin using the Telegram interface! 📱

## 🧪 making cyan files (asdfzxcvb's favorite part)

cyan comes bundled with the `cgen` command, which lets you generate `.cyan` files to pass to `-z`/`--cyan`! 🧬
If you break it, YGB will send you a meme as consolation. 😂

## 🙏 acknowledgements (and roast credits)

- asdfzxcvb: For writing code that even Stack Overflow can't answer. 🤷‍♂️
- YGB: For testing features by running them at 3am and forgetting what he did. 🛌
- tjn: Project maintainer and lead developer. 👨‍💻

---

If you read this far, you deserve a bug-free build. But you won't get one. 🐞 Blame asdfzxcvb. Or YGB. Or both. Enjoy! 🎉

---

If you read this far, you deserve a bug-free build. But you won't get one. Blame Zxc. Or YGB. Or both. Enjoy!

