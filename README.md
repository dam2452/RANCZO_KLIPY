# RanczoKlipy Bot
<img src="Avatar.png" alt="Avatar" width="225"/>

RanczoKlipy Bot to wysoce konfigurowalny bot Telegram, stworzony do zarządzania i przetwarzania klipów wideo z popularnego serialu "Ranczo". Bot umożliwia użytkownikom wyszukiwanie konkretnych cytatów, zarządzanie własnymi klipami wideo oraz wykonywanie różnych zadań administracyjnych związanych z zarządzaniem użytkownikami i moderacją treści.

## Demo Wideo

Zobacz demo wideo, aby zobaczyć, jak działa RanczoKlipy Bot w akcji:

[![Zobacz wideo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

## English Version
For the English version of this README, please refer to [README.md](./READMEen.md).

## Funkcje

### 1. Zarządzanie Klipami Wideo
- **Wyszukiwanie Cytatów:** Użytkownicy mogą wyszukiwać konkretne cytaty z serialu za pomocą komend takich jak `/clip <quote>` i `/search <quote>`. Bot zwróci pasujące fragmenty wideo.
- **Kompilacja Klipów:** Użytkownicy mogą kompilować wiele klipów w jeden plik wideo za pomocą komend takich jak `/compile <clip_numbers>` lub `/compile all`.
- **Dopasowanie Klipów:** Bot umożliwia dopasowanie klipów poprzez regulację czasu rozpoczęcia i zakończenia za pomocą komendy `/adjust <clip_number> <adjust_before> <adjust_after>`.
- **Zarządzanie Zapisanymi Klipami:** Użytkownicy mogą zapisywać, wyświetlać listę i usuwać swoje klipy za pomocą komend takich jak `/save`, `/myclips` i `/deleteclip`.

### 2. Zarządzanie Użytkownikami i Rolami
- **Role Administratora i Moderatora:** Administratorzy i moderatorzy mają dostęp do specjalnych funkcji. Komendy takie jak `/listadmins` i `/listmoderators` pomagają wyświetlić te role.
- **Zarządzanie Listą Dozwolonych Użytkowników:** Użytkownicy mogą być dodawani do lub usuwani z listy dozwolonych, co daje im dostęp do określonych funkcji. Użyj komend `/addwhitelist <user_id>` lub `/removewhitelist <user_id>` w tym celu.
- **Notatki o Użytkownikach:** Administratorzy mogą dodawać notatki do profili użytkowników za pomocą komendy `/note <user_id> <note>`.

### 3. Moderacja Treści
- **Zgłaszanie Problemów:** Użytkownicy mogą zgłaszać problemy bezpośrednio do administratorów za pomocą komendy `/report <issue_description>`.
- **Ograniczenia i Limity:** Aby zapobiec spamowaniu, dla użytkowników niebędących administratorami wprowadzono okresy karencji i limity, co zapewnia zrównoważone korzystanie z bota.

### 4. Integracja z Elasticsearch
- Bot jest zintegrowany z Elasticsearch, co umożliwia efektywne zarządzanie i przeszukiwanie transkrypcji serialu. Ta integracja pozwala na szybkie i dokładne wyszukiwanie segmentów wideo na podstawie zapytań tekstowych.

### 5. Zarządzanie Bazą Danych
- Bot używa PostgreSQL do przechowywania danych użytkowników, klipów wideo, historii wyszukiwań i logów. Operacje na bazie danych, takie jak inicjalizacja schematu i zarządzanie danymi użytkowników, są obsługiwane przez zestaw solidnych funkcji asynchronicznych.

### 6. Dockerized dla Łatwego Wdrożenia
- Bot jest w pełni konteneryzowany za pomocą Docker, co ułatwia jego wdrożenie i uruchomienie na dowolnym systemie. Konfiguracja Docker zapewnia bezproblemowe zarządzanie zależnościami i konfiguracjami.

## Kluczowe Komendy

### Podstawowe Komendy Użytkownika
- **`/start`**: Wyświetla wiadomość powitalną z podstawowymi komendami.
- **`/clip <quote>`**: Wyszukuje konkretny cytat i zwraca pasujący klip wideo.
- **`/myclips`**: Wyświetla listę wszystkich klipów zapisanych przez użytkownika.
- **`/compile <clip_numbers>`**: Kompiluje wybrane klipy w jedno wideo.

### Komendy Administracyjne
- **`/admin`**: Wyświetla komendy administratora.
- **`/listadmins`**: Wyświetla listę wszystkich administratorów.
- **`/listmoderators`**: Wyświetla listę wszystkich moderatorów.
- **`/addwhitelist <user_id>`**: Dodaje użytkownika do listy dozwolonych.
- **`/removewhitelist <user_id>`**: Usuwa użytkownika z listy dozwolonych.
- **`/note <user_id> <note>`**: Dodaje lub aktualizuje notatkę dla użytkownika.
- **`/report <issue_description>`**: Zgłasza problem do administratorów.

Pełna lista komend znajduje się w [Dokumentacji Komend](./COMMANDS.md).

## Wymagania
- **Python 3.12**
- **Baza danych PostgreSQL**
- **Elasticsearch**
- **FFmpeg**

### Wymagane Biblioteki Python
- **ffmpeg**
- **elasticsearch**
- **urllib3**
- **python-dotenv**
- **requests**
- **tabulate**
- **Retry**
- **psycopg2-binary**
- **aiogram**
- **asyncpg**
- **pydantic-settings**
- **pydantic**

## Wkład w Projekt

Wkład w projekt jest zawsze mile widziany! Jeśli chciałbyś pomóc w jego udoskonaleniu, śmiało współpracuj poprzez zgłaszanie pull requestów lub sugerowanie zmian.

## Licencja

Ten projekt jest licencjonowany na podstawie licencji MIT. Możesz używać i modyfikować oprogramowanie do celów osobistych lub wewnętrznych. Jednak dystrybucja lub publiczne udostępnianie zmodyfikowanych wersji powinno odbywać się poprzez wkład w ten projekt. Jeśli chcesz użyć tego oprogramowania w znacznej lub komercyjnej formie, skontaktuj się z twórcami projektu w celu dalszej dyskusji.

## Uzyskaj Dostęp do Bota

Jeśli jesteś zainteresowany dostępem do RanczoKlipy Bot, proszę skontaktuj się ze mną na Telegramie: [@dam2452](https://t.me/dam2452).

## Wesprzyj Projekt

Jeśli podoba Ci się ten projekt i chciałbyś wesprzeć jego rozwój, rozważ postawienie mi kawy:

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/yourprofile)