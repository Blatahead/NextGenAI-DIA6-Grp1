# NextGenAI – DIA6 – Group 1

ESILV, *Next Generation AI / Trustworthy Generative AI* (Topic 1, D. Parisot). Shared repository of the sub-group for TD 1 (21 Oct 2026), TD 2 (18 Nov 2026) and TD 3 (11 Dec 2026).

## Sub-group

**DIA class:** DIA6 · **Sub-group:** DIA6-G1

| Member | Git branch | TD 1 role |
|---|---|---|
| Antonin BIRON | `anto` | Operator E (Dots, OpenRouter account 2); shared repository; checked references C11–C20 |
| Barthélemi STOLTZ | `bart` | Operator D with Emma (Qwen, Groq); wrote references C16–C20 |
| Benjamin ZILBER | `ben` | Operator C (North Mini Code, OpenRouter account 1); checked references C01–C10; merged the common files |
| Emma GOLIARD | `emma` | Operator D with Bart (Qwen, Groq); wrote references C11–C15 |
| Jean-Walter GERARD | `jw` | Operator B (GPT-OSS 20B, Groq); wrote references C06–C10 |
| Noé PAYAN | `noe` | Operator A (GPT-OSS 120B, Groq); wrote references C01–C05 |

TD 1 roles: A, B, C and E each ran one model (20 cells); Emma and Bart ran D together; C and E used two different OpenRouter accounts. Four members wrote the 20 reference queries and two members checked them (`written_by` / `checked_by` in `td1/reference-td1.csv`). Details: `reports/td1.md`, section 9. Roles rotate in TD 2 and TD 3.

## Course pack and environment

- Course pack: **2026-11-18-students-5** (TD 1 run with pack 2026-10-18-students-1; model selection `kit/modeles-autorises.json` of **2026-10-14**). Reference site: https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/index.html
- Database: `kit/data/boutique.sqlite`, seed 20260925, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2` (never modified).
- Python 3.10+ (tested with 3.13.7, SQLite 3.50.4), only extra package: `requests`.
- Models: the five proposed models of 14 Oct 2026 — Groq Free (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`) and OpenRouter free routes (`cohere/north-mini-code:free`, `dots-studio/dots-3-note-preview:free`). No paid access. If a proposed model is replaced by another free model (allowed by the TD 1 assignment), the replacement, its reason and date are documented in `td1/notes/run-notes-td1.md` and `td1/five-model-summary-en.csv`.
- API keys live only in environment variables (`GROQ_API_KEY`, `OPENROUTER_API_KEY`), never in this repository.

## Repository layout

```
README.md            this file
prompts-en.md        experiment prompts verbatim + coding-assistance log
kit/                 course kit shared by the three TDs (scripts find their data next to them)
td1/                 TD 1 deliverables          → td1/README.md
td2/                 TD 2 deliverables          → td2/README.md
  A-quorum/          Step 1, k-of-n vote
  B-consensus/       Step 2, wrong consensus
  C-routing/         Step 3, routing rule
td3/                 TD 3 deliverables          → td3/README.md
reports/             td1.md, td2.md, td3.md (session reports)
topic2-symbolic-ai/  Topic 2 of the module (SymPy exercise notebooks), separate from TD 1–3
```

| Path | Content | Origin |
|---|---|---|
| `kit/skeleton-multi-llm-en.py`, `kit/sandbox_sqlite.py` | Orchestrator and read-only SQLite sandbox (TD 2: `vote_k_sur_n` completed here) | kit |
| `kit/check_access.py`, `kit/verify-data.py` | Environment, access and data-integrity checks | kit |
| `kit/atelier-vote.py`, `kit/atelier-routage.py` | TD 2 workshops (offline; `RESOURCES` and `choose` adapted by Pair C) | kit |
| `kit/schema.sql`, `kit/questions-td1.json`, `kit/modeles-autorises.json` | Schema, the twenty questions, authorised models and parameters | kit |
| `kit/data/` | `boutique.sqlite`, its CSV copies and `manifest.json` (hashes) | kit, unmodified |
| `kit/portefeuille-modeles-2026-09-28.csv` | Model portfolio snapshot (TD 1 summary, TD 3 costs) | kit |
| `kit/templates/` | Blank forms for TD 2 / TD 3 (routing rule, voting tests, costs, contributions) | kit |
| `td1/` | References, raw and merged traces, the two summaries, run notes | ours |
| `td2/A-quorum/`, `td2/B-consensus/`, `td2/C-routing/` | One folder per pair: scripts, outputs and notes of Steps 1, 2 and 3 | ours |
| `reports/td1.md`, `td2.md`, `td3.md` | Session reports | ours |

## Reproduce

From a fresh clone, **commands run from the repository root** (Windows PowerShell: use `python` instead of `python3`, `.venv\Scripts\Activate.ps1` to activate):

```bash
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
python3 -m pip install requests
python3 kit/verify-data.py                 # last object: "ok": true
python3 kit/check_access.py --no-network   # local checks only, no quota used

# TD 1 — keys in environment variables, then (one operator at a time):
python3 kit/skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C02 --reference td1/reference-td1.csv --state td1/state/state-A.jsonl --out td1/traces/traces-A.csv
python3 kit/skeleton-multi-llm-en.py --rates --state td1/state/state-A.jsonl     # rates of one operator
python3 kit/skeleton-multi-llm-en.py --rates --state td1/traces-td1.jsonl        # rates of the five models

# offline
python3 kit/skeleton-multi-llm-en.py --demo        # simulated models, no key (outputs git-ignored)

# TD 2 (offline, on the stored TD 1 traces)
python3 kit/atelier-vote.py                                         # four synthetic examples
python3 kit/atelier-vote.py --traces td1/traces-td1.csv --case C10  # fixed 2-of-3 panel on one question
python3 td2/A-quorum/vote_td2.py                                    # Step 1: tests + 2-of-3 vs 3-of-5 on the twenty questions
python3 td2/B-consensus/wrong-consensus-td2.py                      # Step 2: wrong consensus, delta queries, checks
python3 kit/atelier-routage.py                                      # Step 3: routing simulator (our rule)
```

The skeleton reads `reference-td1.csv` next to itself by default: pass `--reference td1/reference-td1.csv` when scoring, and always pass `--state` / `--out` (their default is the current folder).

_Exact commands actually run (per operator, with dates) are recorded in `td1/notes/run-notes-td1.md`._

## Git workflow

- `main` holds the submitted versions. Each member works on their own branch (`anto`, `bart`, `ben`, `emma`, `jw`, `noe`) and merges into `main` through a pull request.
- Start of each session: `git pull origin main` on your branch.
- Never commit keys, `.env` files, `.venv/` or screenshots showing credentials (see `.gitignore`).

## Hand-ins

| TD | Commit (full hash) | Report | Tag |
|---|---|---|---|
| TD 1 | `cad29357833f4de647db8197a11313f735699e7c` | [`reports/td1.md`](https://github.com/Blatahead/NextGenAI-DIA6-Grp1/blob/cad29357833f4de647db8197a11313f735699e7c/reports/td1.md) | `td1-submission` |
| TD 2 | | | |
| TD 3 | | | |

## Status

- TD 1: _in progress_ — completed work and open blocks are listed in `reports/td1.md`.
