INSERT INTO common_messages (handler_name, key, message)
VALUES
('EpisodeListHandler', 'invalid_args_count', '📋 Podaj poprawną komendę w formacie: /odcinki <sezon>. Przykład: /odcinki 2'),
('EpisodeListHandler', 'no_episodes_found', '❌ Nie znaleziono odcinków dla sezonu {}.');

INSERT INTO common_messages (handler_name, key, message)
VALUES
    ('DeleteClipHandler', 'invalid_args_count', '❌ Podaj numer klipu do usunięcia. Przykład: /usunklip numer_klipu ❌'),
    ('DeleteClipHandler', 'clip_not_exist', '🚫 Klip o numerze {} nie istnieje.🚫'),
    ('DeleteClipHandler', 'clip_deleted', '✅ Klip o nazwie {} został usunięty.✅');

INSERT INTO common_messages (handler_name, key, message) VALUES
('SaveClipHandler', 'clip_name_exists', '⚠️ Klip o takiej nazwie "{}" już istnieje. Wybierz inną nazwę.⚠️'),
('SaveClipHandler', 'no_segment_selected', '⚠️ Najpierw wybierz segment za pomocą /klip, /wytnij lub skompiluj klipy.⚠️'),
('SaveClipHandler', 'failed_to_verify_clip_length', '❌ Nie udało się zweryfikować długości klipu.❌'),
('SaveClipHandler', 'clip_saved_successfully', '✅ Klip "{}" został zapisany pomyślnie. ✅'),
('SaveClipHandler', 'clip_name_not_provided', '📝 Podaj nazwę klipu. Przykład: /zapisz nazwa_klipu'),
('SaveClipHandler', 'clip_name_length_exceeded', '❌ Przekroczono limit długości nazwy klipu.❌'),
('SaveClipHandler', 'clip_limit_exceeded', '❌ Przekroczono limit zapisanych klipów. Usuń kilka starych, aby móc zapisać nowy. ❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('MyClipsHandler','no_saved_clips', '📭 Nie masz zapisanych klipów. 📭');

INSERT INTO common_messages (handler_name, key, message) VALUES
('SearchHandler', 'invalid_args_count', '🔍 Podaj cytat, który chcesz znaleźć. Przykład: /szukaj geniusz');

INSERT INTO common_messages (handler_name, key, message) VALUES
('SearchListHandler', 'no_previous_search_results', '🔍 Nie znaleziono wcześniejszych wyników wyszukiwania.🔍');

INSERT INTO common_messages (handler_name, key, message) VALUES
('TranscriptionHandler', 'no_quote_provided', '🔎 Podaj cytat, który chcesz znaleźć. Przykład: /transkrypcja Nie szkoda panu tego pięknego gabinetu?');

INSERT INTO common_messages (handler_name, key, message) VALUES
('AdjustVideoClipHandler', 'no_previous_searches', '🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.'),
('AdjustVideoClipHandler', 'no_quotes_selected', '⚠️ Najpierw wybierz cytat za pomocą /klip.⚠️'),
('AdjustVideoClipHandler', 'invalid_args_count', '📝 Podaj czas w formacie `<float> <float>` lub `<index> <float> <float>`. Przykład: /dostosuj 10.5 -15.2 lub /dostosuj 1 10.5 -15.2'),
('AdjustVideoClipHandler', 'invalid_interval', '⚠️ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.⚠️'),
('AdjustVideoClipHandler', 'invalid_segment_index', '⚠️ Podano nieprawidłowy indeks cytatu.⚠️'),
('AdjustVideoClipHandler', 'max_extension_limit', '❌ Przekroczono limit rozszerzenia dla komendy dostosuj. ❌'),
('AdjustVideoClipHandler', 'max_clip_duration', '❌ Przekroczono maksymalny czas trwania klipu.❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('AdjustVideoClipHandler', 'extraction_failure', '⚠️ Nie udało się zmienić klipu wideo.');

INSERT INTO common_messages (handler_name, key, message) VALUES
('ClipHandler', 'no_quote_provided', '🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?'),
('ClipHandler', 'no_segments_found', '❌ Nie znaleziono pasujących cytatów.❌'),
('ClipHandler', 'message_too_long', '❌ Wiadomość jest zbyt długa.❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('ClipHandler', 'limit_exceeded_clip_duration', '❌ Przekroczono limit długości klipu.❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('CompileClipsHandler', 'invalid_args_count', '🔄 Proszę podać indeksy cytatów do skompilowania, zakres lub "wszystko" do kompilacji wszystkich segmentów.'),
('CompileClipsHandler', 'invalid_range', '⚠️ Podano nieprawidłowy zakres cytatów: {index} ⚠️'),
('CompileClipsHandler', 'invalid_index', '⚠️ Podano nieprawidłowy indeks cytatu: {index} ⚠️'),
('CompileClipsHandler', 'no_previous_search_results', '🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.'),
('CompileClipsHandler', 'no_matching_segments_found', '❌ Nie znaleziono pasujących cytatów do kompilacji.❌'),
('CompileClipsHandler', 'max_clips_exceeded', '❌ Przekroczono maksymalną liczbę klipów do skompilowania.❌'),
('CompileClipsHandler', 'clip_time_exceeded', '❌ Przekroczono maksymalny czas trwania kompilacji.❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('CompileSelectedClipsHandler', 'invalid_args_count', '📄 Podaj numery klipów do skompilowania w odpowiedniej kolejności.'),
('CompileSelectedClipsHandler', 'no_matching_clips_found', '❌ Nie znaleziono pasujących klipów do kompilacji.❌'),
('CompileSelectedClipsHandler', 'clip_not_found', '❌ Nie znaleziono klipu o numerze {clip_number}.❌'),
('CompileSelectedClipsHandler', 'max_clips_exceeded', '❌ Przekroczono maksymalną liczbę klipów do skompilowania.❌'),
('CompileSelectedClipsHandler', 'clip_time_exceeded', '❌ Przekroczono maksymalny czas trwania kompilacji.❌');


INSERT INTO common_messages (handler_name, key, message) VALUES
('ManualClipHandler', 'invalid_args_count', '📋 **Poprawne użycie komendy**: /wytnij `<sezon_odcinek>` `<czas_start>` `<czas_koniec>`.\nPrzykład: /wytnij S07E06 36:47.50 36:49.00\nUpewnij się, że podałeś poprawnie wszystkie trzy elementy: sezon_odcinek, czas_start i czas_koniec.'),
('ManualClipHandler', 'incorrect_season_episode_format', '❌ **Błędny format sezonu i odcinka!** Użyj formatu **SxxEyy**.\nPrzykład: **S02E10**, gdzie **S02** oznacza sezon 2, a **E10** oznacza odcinek 10.\n🔎 **Zwróć uwagę na dwukropek** między literami S i E oraz na cyfry.'),
('ManualClipHandler', 'video_file_not_exist', '❌ **Nie znaleziono pliku wideo** dla podanego sezonu i odcinka.\nSprawdź, czy podałeś poprawny sezon i odcinek, np. **S02E10**.'),
('ManualClipHandler', 'incorrect_time_format', '❌ **Błędny format czasu!** Użyj formatu **MM:SS\u200B.ms**.\n\nPrzykład: **20:30.11**, gdzie **20:30.11** oznacza 20 minut, 30 sekund i 11 milisekund.\n\n🔎 **Zwróć uwagę na dwukropek** między minutami i sekundami oraz **kropkę** przed milisekundami.'),
('ManualClipHandler', 'end_time_earlier_than_start', '❌ Czas zakończenia musi być późniejszy niż czas rozpoczęcia!\nUpewnij się, że czas_start jest wcześniejszy niż czas_koniec.\nPrzykład: 20:30.11 (czas_start) powinno być wcześniejsze niż 21:32.50 (czas_koniec).'),
('ManualClipHandler', 'limit_exceeded_clip_duration', '❌ Przekroczono limit długości klipu! ❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('BotMessageHandler', 'limit_exceeded_clip_duration', '❌ Przekroczono limit długości klipu! ❌');


INSERT INTO common_messages (handler_name, key, message) VALUES
('SelectClipHandler', 'invalid_args_count', '📋 Podaj numer cytatu, który chcesz wybrać. Przykład: /wybierz 1'),
('SelectClipHandler', 'no_previous_search', '🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.'),
('SelectClipHandler', 'invalid_segment_number', '❌ Nieprawidłowy numer cytatu.❌'),
('SelectClipHandler', 'limit_exceeded_clip_duration', '❌ Przekroczono limit długości klipu.❌');

INSERT INTO common_messages (handler_name, key, message) VALUES
('SendClipHandler', 'clip_not_found_number', '❌ Nie znaleziono klipu o numerze "{}".❌'),
('SendClipHandler', 'clip_not_found_name', '❌ Nie znaleziono klipu o podanej nazwie.❌'),
('SendClipHandler', 'empty_clip_file', '⚠️ Plik klipu jest pusty.⚠️'),
('SendClipHandler', 'empty_file_error', '⚠️ Wystąpił błąd podczas wysyłania klipu. Plik jest pusty.⚠️'),
('SendClipHandler', 'give_clip_name', '📄 Podaj nazwę klipu. Przykład: /wyślij numer_klipu 📄'),
('SendClipHandler', 'limit_exceeded_clip_duration', '❌ Przekroczono limit długości klipu! ❌');


INSERT INTO common_messages (handler_name, key, message) VALUES
('AddSubscriptionHandler', 'no_user_id_provided', '⚠️ Nie podano ID użytkownika ani ilości dni.⚠️'),
('AddSubscriptionHandler', 'subscription_extended', '✅ Subskrypcja dla użytkownika {} przedłużona do {}.✅'),
('AddSubscriptionHandler', 'subscription_error', '⚠️ Wystąpił błąd podczas przedłużania subskrypcji.⚠️');



INSERT INTO common_messages (handler_name, key, message) VALUES
('AddWhitelistHandler', 'no_user_id_provided', '⚠️ Nie podano ID użytkownika.⚠️'),
('AddWhitelistHandler', 'no_username_provided', '✏️ Podaj ID użytkownika.✏️'),
('AddWhitelistHandler', 'user_added', '✅ Dodano {} do whitelisty.✅'),
('AddWhitelistHandler', 'user_not_found', '❌ Nie można znaleźć użytkownika. Upewnij się, że użytkownik rozpoczął rozmowę z botem. ❌');


INSERT INTO common_messages (handler_name, key, message) VALUES
('AdminHelpHandler', 'admin_help', '🛠 Instrukcje dla admina 🛠\n\n═════════════════════════════════\n🔐 Zarządzanie użytkownikami: 🔐\n═════════════════════════════════\n➕ /addwhitelist <id> - Dodaje użytkownika do whitelisty. Przykład: /addwhitelist 123456789\n➖ /removewhitelist <id> - Usuwa użytkownika z whitelisty. Przykład: /removewhitelist 123456789\n📃 /listwhitelist - Wyświetla listę wszystkich użytkowników w whiteliście.\n📃 /listadmins - Wyświetla listę wszystkich adminów.\n📃 /listmoderators - Wyświetla listę wszystkich moderatorów.\n🔑 /klucz <key_content> - Używa klucz dla użytkownika. Przykład: /klucz some_secret_key\n🔑 /listkey - Wyświetla listę wszystkich kluczy.\n🔑 /addkey <days> <note> - Tworzy nowy klucz subskrypcji na X dni. Przykład: /addkey 30 \"tajny_klucz\"\n🚫 /removekey <key> - Usuwa istniejący klucz subskrypcji. Przykład: /removekey some_secret_key\n\n═════════════════════════════════\n💳 Zarządzanie subskrypcjami: 💳\n═════════════════════════════════\n➕ /addsubscription <id> <days> - Dodaje subskrypcję użytkownikowi na określoną liczbę dni. Przykład: /addsubscription 123456789 30\n🚫 /removesubscription <id> - Usuwa subskrypcję użytkownika. Przykład: /removesubscription 123456789\n\n══════════════════════════════════\n🔍 Zarządzanie transkrypcjami: 🔍\n══════════════════════════════════\n🔍 /transkrypcja <cytat> - Wyszukuje cytat w transkrypcjach i zwraca kontekst. Przykład: /transkrypcja Nie szkoda panu tego pięknego gabinetu?\n\n═════════════════════════\n🔎 Dodatkowe komendy: 🔎\n═════════════════════════\n🛠 /admin skroty - Wyświetla skróty komend admina.\n'),
('AdminHelpHandler', 'admin_shortcuts', '🛠 Skróty Komend Admina 🛠\n\n═════════════════════\n📋 Skróty admin 📋\n═════════════════════\n➕ /addw, /addwhitelist <id> - Dodaje użytkownika do whitelisty.\n➖ /rmw, /removewhitelist <id> - Usuwa użytkownika z whitelisty.\n📃 /lw, /listwhitelist - Wyświetla listę użytkowników w whiteliście.\n📃 /la, /listadmins - Wyświetla listę adminów.\n📃 /lm, /listmoderators - Wyświetla listę moderatorów.\n🔑 /klucz, /key <key_content> - Zapisuje nowy klucz dla użytkownika.\n🔑 /lk, /listkey - Wyświetla listę kluczy.\n🔑 /addk, /addkey <days> <note> - Tworzy nowy klucz subskrypcji.\n🚫 /rmk, /removekey <key> - Usuwa istniejący klucz subskrypcji.\n➕ /addsub, /addsubscription <id> <days> - Dodaje subskrypcję użytkownikowi.\n🚫 /rmsub, /removesubscription <id> - Usuwa subskrypcję użytkownika.\n🔍 /t, /transkrypcja <cytat> - Wyszukuje cytat w transkrypcjach.\n');


INSERT INTO common_messages (handler_name, key, message) VALUES
('CreateKeyHandler', 'create_key_usage', '❌ Podaj liczbę dni i klucz. Przykład: /addkey 30 tajny_klucz ❌'),
('CreateKeyHandler', 'create_key_success', '✅ Stworzono klucz: {} na {} dni. ✅'),
('CreateKeyHandler', 'key_already_exists', '❌ Klucz {} już istnieje. ❌');





