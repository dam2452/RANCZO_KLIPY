# Użyj oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.9

# Zaktualizuj listę pakietów i zainstaluj git
RUN apt-get update && apt-get install -y git

# Zainstaluj zależności Pythona
RUN pip install --no-cache-dir elasticsearch gitpython python-telegram-bot moviepy

# Dodaj skrypt, który pobierze najnowszą wersję kodu z repozytorium GitHub przy uruchomieniu kontenera
COPY ./update_and_run.sh /usr/src/app/update_and_run.sh

# Nadaj uprawnienia do wykonania skryptu
RUN chmod +x /usr/src/app/update_and_run.sh

# Ustaw zmienną środowiskową dla repozytorium kodu
ENV CODE_REPO_URL=<url-do-twojego-repozytorium-kodu>

# Ustaw katalog roboczy
WORKDIR /usr/src/app

# Uruchom skrypt aktualizujący i startujący aplikację
CMD ["/usr/src/app/update_and_run.sh"]
