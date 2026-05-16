-- RouterResume – initial schema
-- Run this in Supabase Dashboard → SQL Editor

-- ── profiles ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id         UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    data_md    TEXT         DEFAULT '',
    updated_at TIMESTAMPTZ  DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users own profile"
    ON profiles FOR ALL
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- ── generations ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS generations (
    id              UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID         REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    job_description TEXT,
    resume_text     TEXT,
    model           TEXT,
    filename        TEXT,
    file_docx       TEXT,   -- base64
    file_pdf        TEXT,   -- base64
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

ALTER TABLE generations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users own generations"
    ON generations FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ── reference_resumes ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reference_resumes (
    id           UUID  DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id      UUID  REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    filename     TEXT  NOT NULL,
    file_size    INTEGER,
    file_content TEXT  NOT NULL,   -- base64 of original bytes
    file_text    TEXT  DEFAULT '',  -- extracted plain text (used in prompt)
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE reference_resumes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users own reference_resumes"
    ON reference_resumes FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
