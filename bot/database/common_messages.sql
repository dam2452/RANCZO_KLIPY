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


