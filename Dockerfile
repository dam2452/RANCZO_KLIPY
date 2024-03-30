# Użyj najnowszego oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.10-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Zaktualizuj apt-get i zainstaluj git oraz ffmpeg. Używamy /bin/sh -c aby uruchomić polecenia shella
RUN /bin/sh -c "apt-get update && apt-get install -y --fix-missing git ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*"

# Skopiuj lokalne pliki projektu do kontenera
COPY . /app

# Instalacja zależności Pythona. Ponownie, używamy /bin/sh -c
RUN /bin/sh -c "pip install --no-cache-dir -r requirements.txt"

# Nadaj uprawnienia wykonania skryptowi
RUN chmod +x update_and_run.sh

# Uruchom skrypt przy starcie kontenera. Możemy to zrobić jako część ENTRYPOINT lub CMD, w zależności od potrzeb
ENTRYPOINT ["/bin/sh", "-c", "/app/update_and_run.sh"]

# Ustaw CMD na Bash, co pozwala na interakcję z kontenerem przez Bash, gdy nie jest uruchamiany skrypt
CMD ["/bin/bash"]
