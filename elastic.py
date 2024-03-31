# Importowanie bibliotek
import logging
import os
import urllib3
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env, jeśli istnieje
env_file = os.path.join(os.getcwd(), "passwords.env")  # Ulepszona ścieżka
if os.path.exists(env_file):
    load_dotenv(env_file)

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wyłączenie ostrzeżenia dotyczącego niezaufanych żądań HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Funkcja do nawiązywania połączenia z Elasticsearch
def connect_elastic():
    """
    Funkcja do nawiązywania połączenia z Elasticsearch.
    """
    try:
        es = Elasticsearch(
            [es_host],
            http_auth=(es_username, es_password),
            verify_certs=False,  # Na potrzeby testów, w produkcji należy włączyć
        )
        if not es.ping():
            raise ValueError("Połączenie z Elasticsearch nie powiodło się.")
        logger.info("Połączono z Elasticsearch.")
        return es
    except Exception as e:
        logger.error(f"Nie udało się połączyć z Elasticsearch: {e}")
        return None