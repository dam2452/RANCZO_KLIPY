#!/bin/bash

ln -s /RANCZO-WIDEO ./RANCZO-WIDEO

# Uruchom skrypt Pythona
python /app/telegram_bot.py

# Uruchom Bash
exec "$@"
