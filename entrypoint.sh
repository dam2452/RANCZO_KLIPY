#!/bin/bash

ln -s /RANCZO-WIDEO ./RANCZO-WIDEO
ln -s /RANCZO-TRANSKRYPCJE ./RANCZO-TRANSKRYPCJE

# Uruchom skrypt Pythona
python /app/elastic_manager.py
python /app/telegram_bot.py

# Uruchom Bash
exec "$@"
