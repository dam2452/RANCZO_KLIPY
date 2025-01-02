INSERT INTO common_messages (handler_name, key, message)
VALUES
('EpisodeListHandler', 'invalid_args_count', '📋 Podaj poprawną komendę w formacie: /odcinki <sezon>. Przykład: /odcinki 2'),
('EpisodeListHandler', 'no_episodes_found', '❌ Nie znaleziono odcinków dla sezonu {}.');
INSERT INTO common_messages (handler_name, key, message)
VALUES
    ('DeleteClipHandler', 'invalid_args_count', '❌ Podaj numer klipu do usunięcia. Przykład: /usunklip numer_klipu ❌'),
    ('DeleteClipHandler', 'clip_not_exist', '🚫 Klip o numerze {} nie istnieje.🚫'),
    ('DeleteClipHandler', 'clip_deleted', '✅ Klip o nazwie {} został usunięty.✅');
