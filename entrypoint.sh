#!/bin/bash

ln -s /RANCZO-WIDEO ./RANCZO-WIDEO

# Uruchom skrypt Pythona
python /app/bot.py

# Uruchom Bash
exec "$@"
