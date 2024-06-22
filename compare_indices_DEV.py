from elasticsearch import Elasticsearch

from elasticsearch import Elasticsearch

# Połączenie z pierwszą instancją Elasticsearch
es1 = Elasticsearch(
    ['http://192.168.0.210:30003'],
    basic_auth=('elastic', 'sEbret-wodxob-5kicjo')  # Zaktualizowane na basic_auth
)

# Połączenie z drugą instancją Elasticsearch
es2 = Elasticsearch(
    ['http://192.168.0.210:30034'],
    basic_auth=('elastic', 'sEbret-wodxob-5kicjo')  # Zaktualizowane na basic_auth
)

def get_indices(es):
    """Pobiera listę indeksów z instancji Elasticsearch."""
    return list(es.indices.get_alias(name="*").keys())


def compare_indices(es1, es2):
    """Porównuje indeksy między dwiema instancjami Elasticsearch."""
    indices_es1 = set(get_indices(es1))
    indices_es2 = set(get_indices(es2))

    common_indices = indices_es1.intersection(indices_es2)
    unique_es1 = indices_es1.difference(indices_es2)
    unique_es2 = indices_es2.difference(indices_es1)

    print(f"Wspólne indeksy: {common_indices}")
    print(f"Unikalne dla pierwszej instancji: {unique_es1}")
    print(f"Unikalne dla drugiej instancji: {unique_es2}")

    return common_indices


def compare_documents(es1, es2, index):
    """Porównuje dokumenty w danym indeksie między dwiema instancjami Elasticsearch."""
    count_es1 = es1.count(index=index)['count']
    count_es2 = es2.count(index=index)['count']

    print(f"Porównanie dokumentów w indeksie {index}:")
    print(f"Liczba dokumentów w pierwszej instancji: {count_es1}")
    print(f"Liczba dokumentów w drugiej instancji: {count_es2}")


def main():
    common_indices = compare_indices(es1, es2)
    for index in common_indices:
        compare_documents(es1, es2, index)


if __name__ == "__main__":
    main()
