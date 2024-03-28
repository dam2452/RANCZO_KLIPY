#!/bin/bash

# Ustaw prawidłową wartość URL dla CODE_REPO_URL
CODE_REPO_URL="<url-do-twojego-repozytorium-kodu>"

# Pobierz lub zaktualizuj kod aplikacji
if [ -d "./app" ]; then
  echo "Aktualizacja istniejącego kodu aplikacji..."
  cd ./app
  git pull
else
  echo "Klonowanie kodu aplikacji..."
  git clone ${CODE_REPO_URL} ./app
  cd ./app
fi

# Uruchom aplikację
python indexer.py
