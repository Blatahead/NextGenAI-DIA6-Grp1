# NextGenAI – DIA6 – Group 1

ESILV, *Next Generation AI / Trustworthy Generative AI* (Topic 1, D. Parisot). Shared repository of the sub-group for TD 1 (21 Oct 2026), TD 2 (18 Nov 2026) and TD 3 (11 Dec 2026).

## Sub-group

**DIA class:** DIA6 · **Sub-group:** DIA6-G1

| Member | Git branch | TD 1 role |
|---|---|---|
| Antonin Biron | `anto` | Operator E (Dots, OpenRouter account 2); shared repository; checked references C11–C20 |
| Bart _(full name)_ | `bart` | Operator D with Emma (Qwen, Groq); wrote references C16–C20 |
| Benjamin _(full name)_ | `ben` | Operator C (North Mini Code, OpenRouter account 1); checked references C01–C10; merged the common files |
| Emma _(full name)_ | `emma` | Operator D with Bart (Qwen, Groq); wrote references C11–C15 |
| Jean-Walter _(full name)_ | `jw` | Operator B (GPT-OSS 20B, Groq); wrote references C06–C10 |
| Noé _(full name)_ | `noe` | Operator A (GPT-OSS 120B, Groq); wrote references C01–C05 |

TD 1 roles: A, B, C and E each ran one model (20 cells); Emma and Bart ran D together; C and E used two different OpenRouter accounts. Four members wrote the 20 reference queries and two members checked them (`written_by` / `checked_by` in `reference-td1.csv`). Details: `reports/td1.md`, section 9. Roles rotate in TD 2 and TD 3.

## Course pack and environment

- Course pack: **2026-10-18-students-1** (model selection `modeles-autorises.json` of **2026-10-14**). Reference site: https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/index.html
- Database: `data/boutique.sqlite`, seed 20260925, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2` (never modified).
- Python 3.10+ (tested with 3.13.7, SQLite 3.50.4), only extra package: `requests`.
- Models: the five proposed models of 14 Oct 2026 — Groq Free (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`) and OpenRouter free routes (`cohere/north-mini-code:free`, `dots-studio/dots-3-note-preview:free`). No paid access. If a proposed model is replaced by another free model (allowed by the TD 1 assignment), the replacement, its reason and date are documented in `notes/run-notes-td1.md` and `five-model-summary-en.csv`.
- API keys live only in environment variables (`GROQ_API_KEY`, `OPENROUTER_API_KEY`), never in this repository.

## Repository layout

| Path | Content | Origin |
|---|---|---|
| `skeleton-multi-llm-en.py`, `sandbox_sqlite.py` | Orchestrator and read-only SQLite sandbox (TD 2: `vote_k_sur_n` completed here) | kit |
| `check_access.py`, `verify-data.py` | Environment, access and data-integrity checks | kit |
| `atelier-vote.py`, `atelier-routage.py` | TD 2 workshops (offline) | kit |
| `schema.sql`, `questions-td1.json`, `modeles-autorises.json` | Schema, the twenty questions, authorised models and parameters | kit |
| `data/` | `boutique.sqlite`, its CSV copies and `manifest.json` (hashes) | kit, unmodified |
| `portefeuille-modeles-2026-09-28.csv` | Model portfolio snapshot (TD 1 summary, TD 3 costs) | kit |
| `reference-td1.csv` | **TD 1 step 1**: our reference query and value per question | ours |
| `traces-*.csv`, `state-*.jsonl`, `traces-td1.*` | **TD 1 step 2**: raw traces, every attempt | ours |
| `model-question-comparison-en.csv`, `five-model-summary-en.csv` | **TD 1 step 3**: the two summaries | ours (kit templates) |
| `prompts-en.md` | Experiment prompts verbatim + coding-assistance prompts | ours |
| `notes/` | Run notes: allocation, quota counters, retries, longer explanations | ours |
| `templates/` | Blank forms for TD 2 / TD 3 (routing rule, voting tests, costs, contributions) | kit |
| `reports/td1.md`, `td2.md`, `td3.md` | Session reports | ours |

## Reproduce

From a fresh clone (Windows PowerShell: use `python` instead of `python3`, `.venv\Scripts\Activate.ps1` to activate):

```bash
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
python3 -m pip install requests
python3 verify-data.py                 # last object: "ok": true
python3 check_access.py --no-network   # local checks only, no quota used

# keys in environment variables, then (one operator at a time):
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C02 --state state/state-A.jsonl --out traces/traces-A.csv
python3 skeleton-multi-llm-en.py --rates --state state/state-A.jsonl          # rates of one operator
python3 skeleton-multi-llm-en.py --rates --state traces-td1.jsonl

# offline
python3 skeleton-multi-llm-en.py --demo        # simulated models, no key (outputs git-ignored)
python3 atelier-routage.py
```

_Exact commands actually run (per operator, with dates) are recorded in `notes/run-notes-td1.md`._

## Git workflow

- `main` holds the submitted versions. Each member works on their own branch (`anto`, `bart`, `ben`, `emma`, `jw`, `noe`) and merges into `main` through a pull request.
- Start of each session: `git pull origin main` on your branch.
- Never commit keys, `.env` files, `.venv/` or screenshots showing credentials (see `.gitignore`).

## Hand-ins

| TD | Commit (full hash) | Report | Tag |
|---|---|---|---|
| TD 1 | _to fill_ | [`reports/td1.md`](reports/td1.md) | `td1-submission` |
| TD 2 | | | |
| TD 3 | | | |

## Status

- TD 1: _in progress_ — completed work and open blocks are listed in `reports/td1.md`.
