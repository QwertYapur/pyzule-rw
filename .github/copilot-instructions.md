# Copilot AI Coding Agent Instructions for pyzule-rw

## Project Overview
- **pyzule-rw** is a modern rewrite of [pyzule](https://github.com/asdfzxcvbn/pyzule) for advanced IPA (iOS app) customization, signing, and plugin management.
- The project is modular, with core logic in `cyan/` and supporting scripts/utilities at the repo root.
- Telegram bot integration is a key feature, enabling remote control and status via Telegram.
- Google Drive integration is used for file upload/download automation.

## Major Components
- `cyan/logic.py`: Main entry for IPA processing, orchestrates all customization and signing steps.
- `cyan/tbhtypes/app_bundle.py`: Core class for manipulating app bundles, plugins, and extensions.
- `cyan/drive_utils.py`: Google Drive upload/download utilities, used by the bot and CLI.
- `cyan/telegram_utils.py`: Telegram messaging helpers, used for bot notifications and status.
- `bot.py`: Telegram bot command loop and handlers.
- `convert_to_cyan.py`: Script for converting and signing artifacts into the cyan format.
- `setup.py`: Python packaging and CLI entry points.

## Key Patterns & Conventions
- **AppBundle**: All IPA and plugin manipulations are performed via the `AppBundle` class. Always instantiate with the app path, not just the IPA.
- **Telegram Messaging**: Use `send_telegram_message(chat_id, text, ...)` for all bot notifications. `chat_id` must be provided explicitly.
- **Google Drive**: Use `upload_file_to_drive` and `download_file_from_drive` for file operations. Service account credentials and folder IDs are loaded from environment variables.
- **Error Handling**: Most functions return error strings or log errors; check return values and logs for diagnostics.
- **Environment Variables**: Critical secrets (Google, Telegram) are loaded from env vars, not hardcoded.
- **Type Hints**: Functions use explicit type hints. Match return types exactly (e.g., don't return dict if annotated as str).
- **Modular Utilities**: Utility functions are grouped by domain (e.g., `drive_utils.py`, `telegram_utils.py`).

## Developer Workflows
- **Run the CLI**: `python3 -m cyan.logic ...` or use the `cyan` entry point if installed.
- **Run the Bot**: `python3 bot.py` (ensure all required env vars are set).
- **Build/Install**: `python3 setup.py install` or use pip for local development.
- **Test Google Drive**: Use `drive_test.py` for manual upload/download checks.
- **Debugging**: Use logging output; most modules use `logging.basicConfig` for consistent log formatting.

## Integration Points
- **Telegram**: All bot commands and notifications flow through `bot.py` and `cyan/telegram_utils.py`.
- **Google Drive**: All file storage/retrieval is via `cyan/drive_utils.py`.
- **Signing/Conversion**: `convert_to_cyan.py` and `cyan/logic.py` coordinate signing, entitlements, and IPA mutation.

## Examples
- To send a Telegram message: `send_telegram_message(chat_id, "Build complete!")`
- To upload a file to Drive: `upload_file_to_drive("/path/to/file.ipa")`
- To manipulate an IPA: `app = AppBundle(app_path); app.fakesign_all()`

## Special Notes
- Do not hardcode secrets; always use environment variables.
- When adding new CLI commands or bot features, follow the modular pattern (utility in `cyan/`, handler in `bot.py`).
- If you change function signatures, update all call sites and type hints for consistency.

---

If any section is unclear or missing, please provide feedback for further refinement.
