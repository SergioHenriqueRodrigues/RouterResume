import pytest
from generate import (
    sanitize_filename,
    validate_api_key,
    validate_job_description,
    extract_filename,
    build_prompt,
    mask_api_key,
    LANGUAGES,
    _INTEGRITY_RULES,
)


# ── sanitize_filename ─────────────────────────────────────────────────────────

class TestSanitizeFilename:
    def test_simple_name_unchanged(self):
        assert sanitize_filename("resume.pdf") == "resume.pdf"

    def test_spaces_become_underscores(self):
        assert sanitize_filename("my resume.pdf") == "my_resume.pdf"

    def test_parentheses_become_underscores(self):
        assert sanitize_filename("resume (1).pdf") == "resume__1_.pdf"

    def test_path_traversal_strips_to_filename(self):
        assert sanitize_filename("../../etc/passwd") == "passwd"

    def test_windows_path_strips_to_filename(self):
        assert sanitize_filename(r"C:\Users\john\file.pdf") == "file.pdf"

    def test_empty_string_returns_file(self):
        assert sanitize_filename("") == "file"

    def test_hyphens_and_dots_preserved(self):
        assert sanitize_filename("my-file.v2.pdf") == "my-file.v2.pdf"


# ── validate_api_key ───────────────────────────────────────────────────────────

class TestValidateApiKey:
    def test_valid_key(self):
        assert validate_api_key("sk-or-v1-abc123def456ghi789jkl") is True

    def test_empty_string(self):
        assert validate_api_key("") is False

    def test_none(self):
        assert validate_api_key(None) is False

    def test_wrong_prefix(self):
        assert validate_api_key("sk-abc123def456ghi789") is False

    def test_too_short_after_prefix(self):
        assert validate_api_key("sk-or-") is False

    def test_leading_trailing_whitespace_valid(self):
        assert validate_api_key("  sk-or-v1-abc123def456ghi789  ") is True

    def test_openai_key_rejected(self):
        assert validate_api_key("sk-proj-abc123def456ghi789jkl") is False


# ── validate_job_description ───────────────────────────────────────────────────

class TestValidateJobDescription:
    def test_empty_string(self):
        valid, key = validate_job_description("")
        assert valid is False
        assert key == "no_job_error"

    def test_none(self):
        valid, key = validate_job_description(None)
        assert valid is False
        assert key == "no_job_error"

    def test_whitespace_only(self):
        valid, key = validate_job_description("   \n\t  ")
        assert valid is False
        assert key == "no_job_error"

    def test_too_short(self):
        valid, key = validate_job_description("Dev job")
        assert valid is False
        assert key == "job_too_short"

    def test_exactly_at_length_limit(self):
        valid, key = validate_job_description("x" * 30)
        assert valid is True
        assert key == ""

    def test_valid_description(self):
        desc = "Buscamos desenvolvedor Python sênior com experiência em Django e APIs REST."
        valid, key = validate_job_description(desc)
        assert valid is True
        assert key == ""


# ── extract_filename ───────────────────────────────────────────────────────────

class TestExtractFilename:
    def test_finds_filename_at_end(self):
        text = "Conteúdo do currículo\n\nFILENAME: senior_dev_google"
        clean, slug = extract_filename(text)
        assert slug == "senior_dev_google"
        assert "FILENAME:" not in clean

    def test_no_filename_line_returns_empty_slug(self):
        text = "Currículo sem linha de filename"
        clean, slug = extract_filename(text)
        assert slug == ""
        assert clean == text

    def test_normalizes_accented_chars(self):
        text = "Currículo\nFILENAME: Sênior Développeur"
        _, slug = extract_filename(text)
        assert slug == "senior_developpeur"

    def test_truncates_slug_to_40_chars(self):
        long_name = "a" * 60
        text = f"Currículo\nFILENAME: {long_name}"
        _, slug = extract_filename(text)
        assert len(slug) <= 40

    def test_case_insensitive_keyword(self):
        text = "Currículo\nfilename: backend_engineer_meta"
        _, slug = extract_filename(text)
        assert slug == "backend_engineer_meta"

    def test_spaces_in_filename_become_underscores(self):
        text = "Currículo\nFILENAME: senior backend engineer"
        _, slug = extract_filename(text)
        assert slug == "senior_backend_engineer"

    def test_clean_text_excludes_filename_line(self):
        text = "Nome: João\nExperiência: ...\n\nFILENAME: joao_silva"
        clean, _ = extract_filename(text)
        assert "joao_silva" not in clean
        assert "Nome: João" in clean

    def test_filename_not_confused_in_body(self):
        # FILENAME: only detected near the end (last 8 lines)
        text = "FILENAME: fake_name\n" + ("linha\n" * 20) + "FILENAME: real_name"
        _, slug = extract_filename(text)
        assert slug == "real_name"


# ── mask_api_key ───────────────────────────────────────────────────────────────

class TestMaskApiKey:
    def test_normal_key_shows_last_4(self):
        assert mask_api_key("sk-or-v1-abcdef1234") == "****...1234"

    def test_key_with_4_chars_fully_masked(self):
        assert mask_api_key("abcd") == "****"

    def test_key_shorter_than_4_fully_masked(self):
        assert mask_api_key("ab") == "****"

    def test_key_with_5_chars(self):
        assert mask_api_key("abcde") == "****...bcde"

    def test_strips_whitespace_before_masking(self):
        assert mask_api_key("  sk-or-v1-abcdef1234  ") == "****...1234"


# ── build_prompt ───────────────────────────────────────────────────────────────

class TestBuildPrompt:
    def setup_method(self):
        self.lang_pt = LANGUAGES["1"]
        self.lang_en = LANGUAGES["2"]
        self.lang_es = LANGUAGES["3"]
        self.raw_data = "Nome: João Silva\nEmail: joao@email.com\nPython, Django, 5 anos"
        self.job = "Vaga de desenvolvedor Python sênior com experiência em APIs REST."

    def test_contains_raw_data(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert self.raw_data in prompt

    def test_contains_job_description(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert self.job in prompt

    def test_contains_language_name_portuguese(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert "Portuguese (Brazil)" in prompt

    def test_contains_language_name_english(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_en)
        assert "English" in prompt

    def test_contains_language_name_spanish(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_es)
        assert "Spanish" in prompt

    def test_integrity_rules_injected(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert "DATA INTEGRITY" in prompt
        assert "Do NOT invent" in prompt
        assert "Do NOT fabricate" in prompt

    def test_includes_old_resumes_section_when_provided(self):
        resumes = "[Resume: cv.pdf]\nExperiência anterior em TechCorp"
        prompt = build_prompt(self.raw_data, resumes, self.job, self.lang_pt)
        assert "OLD RESUMES" in prompt
        assert resumes in prompt

    def test_excludes_old_resumes_section_when_empty(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert "OLD RESUMES" not in prompt

    def test_excludes_old_resumes_section_when_whitespace(self):
        prompt = build_prompt(self.raw_data, "   ", self.job, self.lang_pt)
        assert "OLD RESUMES" not in prompt

    def test_portuguese_section_headers(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert "EXPERIÊNCIA PROFISSIONAL" in prompt
        assert "FORMAÇÃO ACADÊMICA" in prompt
        assert "HABILIDADES" in prompt
        assert "RESUMO PROFISSIONAL" in prompt

    def test_english_section_headers(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_en)
        assert "WORK EXPERIENCE" in prompt
        assert "EDUCATION" in prompt
        assert "SKILLS" in prompt
        assert "PROFESSIONAL SUMMARY" in prompt

    def test_spanish_section_headers(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_es)
        assert "EXPERIENCIA PROFESIONAL" in prompt
        assert "FORMACIÓN ACADÉMICA" in prompt
        assert "HABILIDADES" in prompt

    def test_contains_filename_instruction(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert "FILENAME:" in prompt

    def test_skills_section_prohibitions_present(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert "NEVER include" in prompt

    def test_returns_string(self):
        prompt = build_prompt(self.raw_data, "", self.job, self.lang_pt)
        assert isinstance(prompt, str)
        assert len(prompt) > 500


# ── _INTEGRITY_RULES constant ──────────────────────────────────────────────────

class TestIntegrityRules:
    def test_is_string(self):
        assert isinstance(_INTEGRITY_RULES, str)

    def test_contains_key_prohibitions(self):
        assert "Do NOT invent" in _INTEGRITY_RULES
        assert "Do NOT fabricate" in _INTEGRITY_RULES
        assert "Do NOT add" in _INTEGRITY_RULES

    def test_cannot_be_empty(self):
        assert len(_INTEGRITY_RULES.strip()) > 0
