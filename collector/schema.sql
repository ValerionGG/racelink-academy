PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    platform TEXT NOT NULL,
    creator TEXT NOT NULL DEFAULT '',
    language TEXT NOT NULL DEFAULT 'und',
    category TEXT NOT NULL DEFAULT 'other',
    domain_scope TEXT NOT NULL DEFAULT 'motorsport',
    pedagogical_format TEXT NOT NULL DEFAULT 'unspecified',
    level TEXT NOT NULL DEFAULT 'all',
    description TEXT NOT NULL DEFAULT '',
    duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
    published_at TEXT,
    thumbnail_url TEXT,
    tags TEXT NOT NULL DEFAULT '[]',
    license TEXT NOT NULL DEFAULT 'unknown',
    license_url TEXT,
    source_url TEXT NOT NULL,
    verified_at TEXT,
    review_status TEXT NOT NULL DEFAULT 'candidate',
    verification_scope TEXT NOT NULL DEFAULT 'public_search_metadata',
    language_status TEXT NOT NULL DEFAULT 'unknown',
    level_status TEXT NOT NULL DEFAULT 'estimated',
    transcript_text TEXT NOT NULL DEFAULT '',
    source_questions_text TEXT NOT NULL DEFAULT '',
    transcript_language TEXT,
    transcript_source_url TEXT,
    transcript_permission_basis TEXT,
    transcript_permission_reference TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_videos_category ON videos(category);
CREATE INDEX IF NOT EXISTS idx_videos_language ON videos(language);
CREATE INDEX IF NOT EXISTS idx_videos_platform ON videos(platform);
CREATE INDEX IF NOT EXISTS idx_videos_level ON videos(level);
CREATE INDEX IF NOT EXISTS idx_videos_published ON videos(published_at);
CREATE INDEX IF NOT EXISTS idx_videos_license ON videos(license);
CREATE VIRTUAL TABLE IF NOT EXISTS videos_fts USING fts5(
    title, creator, description, tags, transcript_text, source_questions_text,
    content='videos', content_rowid='rowid',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS videos_ai AFTER INSERT ON videos BEGIN
    INSERT INTO videos_fts(rowid,title,creator,description,tags,transcript_text,source_questions_text)
    VALUES(new.rowid,new.title,new.creator,new.description,new.tags,new.transcript_text,new.source_questions_text);
END;
CREATE TRIGGER IF NOT EXISTS videos_ad AFTER DELETE ON videos BEGIN
    INSERT INTO videos_fts(videos_fts,rowid,title,creator,description,tags,transcript_text,source_questions_text)
    VALUES('delete',old.rowid,old.title,old.creator,old.description,old.tags,old.transcript_text,old.source_questions_text);
END;
CREATE TRIGGER IF NOT EXISTS videos_au AFTER UPDATE OF title,creator,description,tags,transcript_text,source_questions_text ON videos BEGIN
    INSERT INTO videos_fts(videos_fts,rowid,title,creator,description,tags,transcript_text,source_questions_text)
    VALUES('delete',old.rowid,old.title,old.creator,old.description,old.tags,old.transcript_text,old.source_questions_text);
    INSERT INTO videos_fts(rowid,title,creator,description,tags,transcript_text,source_questions_text)
    VALUES(new.rowid,new.title,new.creator,new.description,new.tags,new.transcript_text,new.source_questions_text);
END;
CREATE TABLE IF NOT EXISTS video_vehicles (
    id INTEGER PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    make TEXT NOT NULL DEFAULT '', make_key TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '', model_key TEXT NOT NULL DEFAULT '',
    generation TEXT NOT NULL DEFAULT '', generation_key TEXT NOT NULL DEFAULT '',
    engine TEXT NOT NULL DEFAULT '', engine_key TEXT NOT NULL DEFAULT '',
    body_type TEXT NOT NULL DEFAULT '', body_type_key TEXT NOT NULL DEFAULT '',
    fuel_type TEXT NOT NULL DEFAULT '', fuel_type_key TEXT NOT NULL DEFAULT '',
    year_from INTEGER, year_to INTEGER,
    evidence TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'title_mention',
    UNIQUE(video_id,position)
);
CREATE INDEX IF NOT EXISTS idx_vehicle_video ON video_vehicles(video_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_application ON video_vehicles(make_key,model_key,generation_key,engine_key);
CREATE INDEX IF NOT EXISTS idx_vehicle_model ON video_vehicles(model_key);
CREATE INDEX IF NOT EXISTS idx_vehicle_engine ON video_vehicles(engine_key);
CREATE INDEX IF NOT EXISTS idx_vehicle_body ON video_vehicles(body_type_key);
CREATE INDEX IF NOT EXISTS idx_vehicle_fuel ON video_vehicles(fuel_type_key);
CREATE TABLE IF NOT EXISTS video_tasks (
    video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    task TEXT NOT NULL, PRIMARY KEY(video_id,task)
);
CREATE INDEX IF NOT EXISTS idx_tasks_task ON video_tasks(task,video_id);
CREATE TABLE IF NOT EXISTS video_systems (
    video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    system TEXT NOT NULL, PRIMARY KEY(video_id,system)
);
CREATE INDEX IF NOT EXISTS idx_systems_system ON video_systems(system,video_id);
CREATE TABLE IF NOT EXISTS video_specifications (
    id INTEGER PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    kind TEXT NOT NULL, value TEXT NOT NULL, value_key TEXT NOT NULL,
    evidence TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'title_mention'
);
CREATE INDEX IF NOT EXISTS idx_specifications_value ON video_specifications(value_key,video_id);
CREATE INDEX IF NOT EXISTS idx_specifications_video ON video_specifications(video_id);
CREATE TABLE IF NOT EXISTS import_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    inserted INTEGER NOT NULL,
    updated INTEGER NOT NULL,
    rejected INTEGER NOT NULL,
    errors_json TEXT NOT NULL DEFAULT '[]'
);
