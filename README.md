# Yearbook Dataset

Research dataset for studying gendered language patterns in US college yearbooks (1901–1930). This repository contains extracted yearbook data, OCR tooling, and yearbook collection records.

## Quick start

```bash
conda activate Yearbook_Project
pip install openai
```

### Run OCR on a yearbook page image

```bash
export OCR_API_KEY="your-api-key"
python code/ocr.py --image path/to/page.jpg --mode 3 --output result.csv
```

Three OCR modes:
- `--mode 1`: Traditional Chinese vertical text
- `--mode 2`: Table gender classification (all-male / all-female / coed)
- `--mode 3` (default): Statistical table → CSV

## Repository structure

```
├── README.md
├── DATASET_CONSTRUCTION.md              # Full documentation
├── .gitignore
│
├── code/
│   └── ocr.py                           # OCR extraction (OpenAI Vision API)
│
├── text_data.json                       # Raw OCR'd yearbook text (~17K records, 20 MB)
│
├── all_data/                            # Per-school, per-year JSON with dimension scores
│   ├── schools_index.json
│   └── {University}/{year}.json         # 202 files across 22 schools, 21 MB
│
├── all_data_by Univ_adjusted_final/     # Raw extracted yearbook data (no scores)
│   └── {University}/{University}_{year}.json  # 202 files across 22 schools, 14 MB
│
└── new_yearbook/                        # Yearbook PDF collection records (no PDFs)
    ├── PROJECT_SUMMARY.md               # Collection project overview
    ├── SESSION_SUMMARY_*.md             # Daily session summaries
    ├── *_LOG.md                         # Per-university search logs
    └── OPTIMIZED_PROMPT.md              # Prompt template for finding yearbooks
```

## Key data files

| Directory / File | Size | Files | Description |
|------------------|------|:-----:|-------------|
| `all_data/` | 21 MB | 202 | Merged data with dimension scores (Appearance, Character/Personality, Ability) + OCR text |
| `all_data_by Univ_adjusted_final/` | 14 MB | 202 | Raw extracted yearbook data (structured fields, no scores) |
| `text_data.json` | 20 MB | 1 | Raw OCR'd yearbook entry text per student |

### Data schema

**`all_data/`** — each record:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Student name |
| `gender` | string | Male / Female |
| `year` | int | Yearbook year (1901–1930) |
| `University` | string | University name |
| `major` | string | Class year / major |
| `text` | string | OCR'd yearbook entry text |
| `description` | string | Extracted description (subset of text) |
| `Appearance` | float | Appearance dimension score (0–1) |
| `Character_Personality` | float | Character/personality score (0–1) |
| `Ability` | float | Ability score (0–1) |

Plus metadata fields: `nicknames`, `high school`, `motto`, `birthday`, `hometown`, `enrolltime`, `clubs`.

**`all_data_by Univ_adjusted_final/`** — same fields as above minus `University`, `year`, `text`, `Appearance`, `Character_Personality`, `Ability`.

## University coverage

22 universities, ~200 school-year combinations across 1901–1930. See `all_data/schools_index.json` for the full list.

## Yearbook PDFs

Downloaded yearbook PDFs (~10 GB, 264 volumes across 14 universities) are stored on Google Drive, not in this repo. Collection progress and search logs are in `new_yearbook/`.

## Environment

```bash
conda activate Yearbook_Project
```

Key dependency: `openai`.
