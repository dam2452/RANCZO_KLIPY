#!/bin/bash

# Zdefiniuj zmienne dla repozytoriów
KLIPY_REPO_DIR="/app"
TRANSKRYPCJE_REPO_DIR="/RANCZO-TRANSKRYPCJE"

# Aktualizacja repozytorium RANCZO_KLIPY
cd $KLIPY_REPO_DIR
git pull

# Klonowanie lub aktualizacja repozytorium RANCZO-TRANSKRYPCJE
if [ -d "$TRANSKRYPCJE_REPO_DIR" ]; then
    echo "Aktualizacja repozytorium RANCZO-TRANSKRYPCJE..."
    cd $TRANSKRYPCJE_REPO_DIR
    git pull
else
    echo "Klonowanie repozytorium RANCZO-TRANSKRYPCJE..."
    git clone https://github.com/dam2452/RANCZO-TRANSKRYPCJE.git $TRANSKRYPCJE_REPO_DIR
fi

# Powrót do katalogu z botem
cd $KLIPY_REPO_DIR

# Uruchom bota
python bot.py
