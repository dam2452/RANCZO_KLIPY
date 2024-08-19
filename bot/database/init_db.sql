CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    subscription_end DATE DEFAULT NULL
);


CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_profiles(id),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_moderator BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT unique_user_id UNIQUE(user_id)
);


CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL,
    user_id INT REFERENCES user_profiles(id),
    command TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);


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
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS video_clips (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    user_id INT NOT NULL REFERENCES user_profiles(id),
    clip_name TEXT NOT NULL,
    video_data BYTEA NOT NULL,
    start_time FLOAT,
    end_time FLOAT,
    duration FLOAT,
    season INT,
    episode_number INT,
    is_compilation BOOLEAN NOT NULL DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES user_profiles(id),
    report TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    quote TEXT NOT NULL,
    segments JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS last_clips (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    segment JSONB,
    compiled_clip BYTEA,
    type TEXT,
    adjusted_start_time FLOAT NULL,
    adjusted_end_time FLOAT NULL,
    is_adjusted BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);



CREATE OR REPLACE FUNCTION clean_old_last_clips() RETURNS trigger AS $$
BEGIN
    DELETE FROM last_clips WHERE timestamp < NOW() - INTERVAL '30 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_clean_last_clips
AFTER INSERT ON last_clips
FOR EACH ROW EXECUTE FUNCTION clean_old_last_clips();


CREATE OR REPLACE FUNCTION clean_old_search_history() RETURNS trigger AS $$
BEGIN
    DELETE FROM search_history WHERE timestamp < NOW() - INTERVAL '30 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_clean_search_history
AFTER INSERT ON search_history
FOR EACH ROW EXECUTE FUNCTION clean_old_search_history();
