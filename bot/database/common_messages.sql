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
