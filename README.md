### Phase 0 — Experimentation (validate before building)

Each experiment is a standalone script in `/experiments`. No DB, no API, no
UI — just run it, read the output, decide keep / tweak / cut.

- [/] **Experiment 1 — RSS data quality check**
  Pull raw RSS from Rappler, Inquirer, GMA News. Print title, summary,
  timestamp, source. Check for encoding issues, missing fields, inconsistent
  formats.
  → `experiments/01_rss_quality_check.py`

- [/] **Experiment 2 — AI summarization quality**
  Take 5 real articles from Experiment 1, summarize with Gemini (free tier).
  Check handling of Taglish/local terms, tone, accuracy, length.
  → `experiments/02_summarization_check.py`

- [/] **Experiment 3 — Trending signal check**
  Pull Reddit r/Philippines hot posts + Google Trends PH side by side.
  Assess whether this data is genuinely useful trending signal or just noise.
  → `experiments/04_trending_signal_check.py`

- [/] **Experiment 4 — Daily digest generation**
  Feed Gemini 5–8 summarized stories from the day, generate a written daily
  briefing. Check tone, length, and usefulness.
  → `experiments/05_digest_check.py`