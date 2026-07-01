# Yearbook Dataset: Construction & Collection

## Overview

This repository contains extracted yearbook data, an OCR pipeline, and yearbook collection records for a research project studying gendered language patterns in US college yearbooks (1901–1930).

The analysis pipeline (regression, visualization, NLP gender scoring) lives in a separate repository. This repo contains only the data layer and text extraction tooling.

---

## Part 1: Yearbook Collection Progress

### Collection Summary (April 30 – May 2, 2026)

| Metric | Value |
|--------|-------|
| Target universities | 18 |
| Successfully acquired | **14 / 18** |
| Confirmed unavailable | 4 |
| Total volumes downloaded | **264** |
| Total data size | **~10 GB** |

### Detailed Results

#### Complete / Near-Complete (11 schools)

| University | Volumes | Size | Year Coverage | Source |
|------------|:-------:|------|---------------|--------|
| William & Mary | 29 | 329 MB | 1901–1930 (no 1904) | Internet Archive |
| Tulane | 29 | 673 MB | 1902–1930 | Internet Archive |
| Johns Hopkins | 29 | 3.0 GB | 1900–1930 (no 1910–11) | JScholarship |
| Austin College | 28 | 1.9 GB | 1903–1930 | Internet Archive |
| Georgia (UGA) | 28 | 884 MB | 1901–1930 (no 1908, 1916) | DLG |
| William Jewell | 25 | 341 MB | 1905–1930 (no 1926) | digitalmobius.org |
| Florida State | 18 | 332 MB | 1901–1930 | Internet Archive |
| NC Women (UNCG) | 18 | 378 MB | 1902–1930 | Internet Archive |
| Howard College | 13 | 173 MB | 1912–1930 | Internet Archive |
| Rockford College | 22 | 263 MB | 1903–1930 | Internet Archive |
| Loyola New Orleans | 7 | 97 MB | 1924–1930 | Internet Archive |

#### Partial (1 school)

| University | Volumes | Size | Notes |
|------------|:-------:|------|-------|
| Columbia | 2 | 16 MB | HathiTrust has 15 PD volumes but requires member institution |

#### Small Acquisitions (2 schools)

| University | Volumes | Size | Source |
|------------|:-------:|------|--------|
| Xavier | 7 | 146 MB | Mixed sources |
| Lander | 8 | 1.1 GB | scmemory.org → CONTENTdm JP2 |

#### Confirmed Unavailable (4 schools)

| University | Yearbook Name | Reason |
|------------|---------------|--------|
| Fordham | The Maroon | Not digitized (Fordham Archives only, physical) |
| Virginia Union | The Panther | First published 1940s; no yearbook in 1901–1930 |
| Blue Mountain | — | Only published course catalogues, no yearbook |
| CCNY | The Microcosm | e-yearbook.com paywall + NYPL physical only |

### Core Gap

**Columbia University** is the biggest miss — HathiTrust holds 15 public-domain volumes but restricts full-PDF download to member institutions. A .edu email or interlibrary loan could recover these.

### Download Methods

| Method | Target Site | Notes |
|--------|-------------|-------|
| `curl` + HTTP proxy | Internet Archive direct links | Primary method; 10–15s interval to avoid 429 |
| IA Advanced Search API | Internet Archive | Used to verify identifiers before download |
| `curl_cffi` (Chrome 120 impersonation) | JScholarship (JHU DSpace) | Successfully bypassed Cloudflare |
| Manual browser download | digitalmobius.org (Hyku JS-rendered) | Only viable method for Hyku sites |
| `curl_cffi` + session cookies | HathiTrust | Failed: Cloudflare + member wall |

### PDF Storage Note

The downloaded yearbook PDFs (~10 GB) are stored on Google Drive, **not in this repository**. This repo contains only the extracted text, structured data, and search logs.

Search logs for each university are in `new_yearbook/` (e.g., `Tulane_University_LOG.md`).

---

## Part 2: Dataset Construction Pipeline

### Architecture

```
Yearbook PDFs (Google Drive)
        │
        ▼
┌──────────────────┐
│  code/ocr.py     │  OpenAI Vision API (gemini-3-flash-preview)
│  OCR extraction  │  via jeniya.cn proxy
└──────────────────┘
        │
        ▼
  text_data.json    (~20 MB, ~17K records)
  Raw OCR'd yearbook text per person
        │
        ▼
┌────────────────────────────────────┐
│  Data extraction & scoring         │  (in main analysis repo)
│  - Structured field extraction     │
│  - Dimension scoring (Appearance,  │
│    Character/Personality, Ability) │
└────────────────────────────────────┘
        │
        ├──────────────────────────────┐
        ▼                              ▼
  all_data/                  all_data_by Univ_adjusted_final/
  With dimension scores      Raw extracted fields (no scores)
  + OCR text                 + metadata
```

### Data Files

#### `text_data.json`

Raw OCR output. Each record has: `name`, `gender`, `year`, `University`, `text`, `image` (source reference). This is the direct output of the OCR pipeline — unprocessed yearbook text as transcribed by the vision model.

#### `all_data/` (merged dataset with dimension scores)

Per-school, per-year JSON files under `{University}/{year}.json`. Each record contains:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Student name |
| `gender` | string | Male / Female |
| `year` | int | Yearbook year (1901–1930) |
| `University` | string | University name |
| `major` | string | Class year / major |
| `text` | string | Full OCR'd yearbook entry text |
| `description` | string | Extracted description portion |
| `Appearance` | float | Appearance dimension score (0–1) |
| `Character_Personality` | float | Character/personality score (0–1) |
| `Ability` | float | Ability score (0–1) |
| `nicknames` | list | Nicknames |
| `high school` | string | High school attended |
| `motto` | string | Personal motto |
| `birthday` | string | Birth date |
| `hometown` | string | Home town |
| `enrolltime` | string | Enrollment year |
| `clubs` | list | Clubs and activities |

The three dimension scores (Appearance, Character/Personality, Ability) quantify how much the yearbook text focuses on each dimension:
- **Appearance** — Physical appearance descriptions
- **Character/Personality** — Character traits, personality
- **Ability** — Academic/professional capability

#### `all_data_by Univ_adjusted_final/` (raw extracted data)

Same structure as `all_data/` but **without** the fields `University`, `year`, `text`, `Appearance`, `Character_Personality`, `Ability`. Contains only the raw structured fields extracted from yearbook entries (name, gender, metadata, description).

Files are named `{University}/{University}_{year}.json` (flat naming within per-school directories).

### University Coverage

22 universities across ~200 school-year combinations (1901–1930):

- Arkansas Tech University
- Clemson University
- East Carolina University
- Georgia Southern University
- Iowa State University
- Kent State University
- Kentucky State University
- Missouri University of Science and Technology
- New Mexico State University
- Southern Arkansas University
- University of Arizona
- University of Arkansas
- University of Florida
- University of Idaho
- University of Mississippi
- University of Nevada
- University of New Hampshire
- University of North Dakota
- University of Southern Mississippi
- Utah State University
- Virginia Tech (VPI)
- Washington State University

Note: These 22 schools (from US Bureau of Education statistical tables) are a **different set** from the 18 schools targeted for yearbook PDF collection. The PDF collection aimed at schools with known single-sex-to-coed transition timelines; the dimension dataset comes from a broader national statistical survey.

---

## Part 3: Repository Structure

```
yearbook-data-repo/
├── README.md                               # Quick-start guide
├── DATASET_CONSTRUCTION.md                 # This document
├── .gitignore
│
├── code/
│   └── ocr.py                              # OCR script (OpenAI Vision API)
│
├── text_data.json                          # Raw OCR'd yearbook text (~17K records, 20 MB)
│
├── all_data/                               # Merged data with dimension scores
│   ├── schools_index.json                  # School → year index
│   └── {University}/{year}.json            # 202 files, 21 MB
│
├── all_data_by Univ_adjusted_final/        # Raw extracted data without scores
│   └── {University}/{University}_{year}.json  # 202 files, 14 MB
│
└── new_yearbook/                           # Yearbook PDF collection records
    ├── PROJECT_SUMMARY.md                  # Collection project overview
    ├── SESSION_SUMMARY_*.md                # Daily session summaries
    ├── *_LOG.md                            # Per-university search logs
    ├── list_of_institutions.txt            # Target institution list
    └── OPTIMIZED_PROMPT.md                 # Prompt template for finding yearbooks
```

### What's NOT in this repo

- **Yearbook PDFs** — ~10 GB, stored on Google Drive
- **Analysis code** — regression scripts, NLP gender scoring, LLM rescoring pipeline, figure generation
- **Original source data** — US Bureau of Education Excel files, processed CSVs, intermediate merge files
- **Built artifacts** — HTML viewer, PNG figures

---

## Part 4: Environment

```bash
conda activate Yearbook_Project
pip install openai
```

Only `openai` is needed for the OCR script in this repo.
