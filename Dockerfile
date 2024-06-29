# Wybór obrazu bazowego
FROM python:3.12-slim

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików do kontenera
COPY . .

# Instalacja zależności Pythona z pliku requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -ms /bin/bash ranczo-klipy
USER ranczo-klipy

ENV PYTHONUNBUFFERED=1

# Ustawienie domyślnej komendy do uruchomienia
CMD ["python", "-m", "bot.bot"]
