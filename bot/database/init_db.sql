CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT PRIMARY KEY,
    username TEXT UNIQUE,
    full_name TEXT,
    subscription_end DATE DEFAULT NULL,
    note TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles (user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles (username);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id BIGINT PRIMARY KEY REFERENCES user_profiles(user_id),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_moderator BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_admin ON user_roles (is_admin);
CREATE INDEX IF NOT EXISTS idx_user_roles_moderator ON user_roles (is_moderator);

CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    command TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (timestamp);

CREATE INDEX IF NOT EXISTS idx_user_logs_user_id ON user_logs(user_id);

CREATE TABLE IF NOT EXISTS user_logs_y2023 PARTITION OF user_logs
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE IF NOT EXISTS user_logs_y2024 PARTITION OF user_logs
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS user_logs_y2025 PARTITION OF user_logs
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    log_level TEXT NOT NULL,
    log_message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);

CREATE TABLE IF NOT EXISTS video_clips (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    clip_name TEXT NOT NULL,
    video_data BYTEA NOT NULL,
    start_time FLOAT,
    end_time FLOAT,
    duration FLOAT,
    season INT,
    episode_number INT,
    is_compilation BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_video_clips_user_id ON video_clips(user_id);
CREATE INDEX IF NOT EXISTS idx_video_clips_clip_name ON video_clips(clip_name);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    report TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);

CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    quote TEXT NOT NULL,
    segments JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_history_timestamp ON search_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_search_history_quote ON search_history USING gin(quote gin_trgm_ops);

CREATE TABLE IF NOT EXISTS last_clips (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    segment JSONB,
    compiled_clip BYTEA,
    type TEXT,
    adjusted_start_time FLOAT NULL,
    adjusted_end_time FLOAT NULL,
    is_adjusted BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_last_clips_timestamp ON last_clips(id);
CREATE INDEX IF NOT EXISTS idx_last_clips_timestamp ON last_clips(chat_id);

CREATE TABLE IF NOT EXISTS user_keys (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    message_content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_messages_user_id ON user_keys (user_id);

CREATE OR REPLACE FUNCTION clean_old_last_clips() RETURNS trigger AS $$
BEGIN
    DELETE FROM last_clips WHERE timestamp < NOW() - INTERVAL '365 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_clean_last_clips'
    ) THEN
        CREATE TRIGGER trigger_clean_last_clips
        AFTER INSERT ON last_clips
        FOR EACH ROW EXECUTE FUNCTION clean_old_last_clips();
    END IF;
END $$;

CREATE OR REPLACE FUNCTION clean_old_search_history() RETURNS trigger AS $$
BEGIN
    DELETE FROM search_history WHERE timestamp < NOW() - INTERVAL '365 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_clean_search_history'
    ) THEN
        CREATE TRIGGER trigger_clean_search_history
        AFTER INSERT ON search_history
        FOR EACH ROW EXECUTE FUNCTION clean_old_search_history();
    END IF;
END $$;

CREATE OR REPLACE FUNCTION clean_old_user_keys() RETURNS trigger AS $$
BEGIN
    DELETE FROM user_keys WHERE timestamp < NOW() - INTERVAL '7 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_clean_user_keys'
    ) THEN
        CREATE TRIGGER trigger_clean_user_keys
        AFTER INSERT ON user_keys
        FOR EACH ROW EXECUTE FUNCTION clean_old_user_keys();
    END IF;
END $$;

