# festy-crew

Two-phase CrewAI agent system for discovering indie-pop-aligned Asian music festivals and enriching approved entries with organizer contact details.

## How it works

**Phase 1** — Research: agents search and score festivals, outputting a CSV for manual review.
**Phase 2** — Enrich: agents find organizer emails for the festivals you approved.

## Setup

```bash
uv sync
cp .env.example .env
# Fill in your API keys in .env
```

### API keys

| Key | Required | Purpose |
|-----|----------|---------|
| `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` | Yes | LLM (one or the other) |
| `FIRECRAWL_API_KEY` | Yes | Web scraping |
| `HUNTER_API_KEY` | No | Email lookup (degrades gracefully if absent) |

Set `MODEL` to override the default (e.g. `gpt-4o`, `claude-sonnet-4-6`).

## Usage

```bash
# Phase 1: discover festivals
uv run python phase1.py
# → festivals_phase1.csv

# Open the CSV and add "Yes" in the Approved column for festivals you want

# Phase 2: enrich with contact emails
uv run python phase2.py festivals_phase1.csv
# → festivals_phase2_enriched.csv
```
