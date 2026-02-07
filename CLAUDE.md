# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**etc-otp** is a desktop TOTP (Time-based One-Time Password) manager built with Python and PyQt6. It stores OTP secrets in a local SQLite database and supports QR code scanning (from files and clipboard). The UI is in Korean.

## Running the Application

```bash
python main.py
```

The app can also be built into a standalone executable via PyInstaller (a `build/` directory exists with PyInstaller artifacts).

## Dependencies

No requirements.txt exists. Key dependencies that must be installed:

- **PyQt6** - GUI framework
- **pyotp** - TOTP generation
- **pyzbar** - QR code decoding (requires the zbar shared library installed on the system)
- **qrcode** - QR code generation
- **Pillow** - Image handling and clipboard image conversion

## Architecture

The app follows a separation between UI layout and application logic:

- **`main.py`** - Entry point and application logic (`OTPApp` class). Initializes the DB, wires up all signal/slot connections, and contains all business logic methods (add/update/rename/delete sites, OTP generation, export/import, QR scanning).
- **`ui_main.py`** - Pure UI layout definition (`Ui_OTPApp` class). Defines all widgets and layout using PyQt6 — no logic here. `OTPApp` in `main.py` instantiates this and connects signals.
- **`module/db_manager.py`** - SQLite database layer. Single table `secrets` with columns `(id, site_name UNIQUE, secret_key)`. Each function opens/closes its own connection. DB file (`otp_secrets.db`) is placed next to the executable/script.
- **`module/otp_manager.py`** - OTP generation. Handles both raw Base32 secrets and `otpauth://` URIs by parsing the secret parameter out of the URI before passing to `pyotp.TOTP`.
- **`module/qr_handler.py`** - QR code decode (from file path or PIL Image) and encode using pyzbar/qrcode libraries.

## Key Behaviors

- Secrets are stored as-is in the DB (can be Base32 strings or full `otpauth://` URIs). Parsing happens at OTP generation time in `parse_secret()`.
- Clicking a site in the list generates the OTP, copies it to clipboard, and starts a countdown timer showing remaining validity.
- **Ctrl+V** is overridden globally: if the clipboard contains an image, the app attempts to decode it as a QR code and add the site.
- Export/import uses JSON format with `{id, site_name, secret_key}` objects.
- Dark mode is enabled by default on startup.
