# Użyj najnowszego oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.10-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Zaktualizuj apt-get i zainstaluj potrzebne pakiety
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj wszystkie pliki projektu do kontenera, z wyjątkiem tych zdefiniowanych w .dockerignore
COPY . .

# Instalacja zależności Pythona z pliku requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj skrypt entrypoint do kontenera
COPY entrypoint.sh /entrypoint.sh

# Nadaj uprawnienia wykonania skryptowi entrypoint
RUN chmod +x /entrypoint.sh

# Ustaw skrypt entrypoint.sh jako punkt wejścia
ENTRYPOINT ["/entrypoint.sh"]

# Domyślnie uruchom Bash po zakończeniu pracy skryptu entrypoint
CMD ["/bin/bash"]
