# JobFit-AI-MVP

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="Python 3.11+">
  </a>
  <a href="https://github.com/CampoyLira1994/JobFit-AI-MVP/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/CampoyLira1994/JobFit-AI-MVP/issues">
    <img src="https://img.shields.io/github/issues/CampoyLira1994/JobFit-AI-MVP" alt="GitHub issues">
  </a>
</p>

JobFit-AI-MVP is a Python MVP for finding, consolidating, and scoring job openings against a configurable candidate profile. It focuses on electrical engineering and field-supervision roles, with explicit checks for salary fit, location fit, role relevance, missing requirements, and red flags that should not be overstated in a CV or application.

The project does not apply to jobs automatically. It ranks opportunities, exports analysis, and helps decide which applications deserve manual review.

## What It Does

- Searches job sources through API-based agents such as Adzuna and SerpAPI Google Jobs.
- Normalizes and deduplicates vacancies across sources.
- Scores technical fit, salary fit, location fit, and role relevance.
- Detects restrictions such as title-in-progress, professional license claims, certifications, unsupported tools, and relocation conflicts.
- Separates local ZMVM openings from broader Estado de Mexico locations that need distance validation.
- Exports ranked results to JSON and CSV.
- Keeps the legacy FastAPI backend and scraper modules available for future integration work.

## Quick Start

```powershell
git clone https://github.com/CampoyLira1994/JobFit-AI-MVP.git
cd JobFit-AI-MVP

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Create a local `.env` file from `.env.example` and fill only the services you plan to use.

```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
ADZUNA_COUNTRY=mx

SERPAPI_API_KEY=your_serpapi_key
SERPAPI_GOOGLE_DOMAIN=google.com.mx
SERPAPI_GL=mx
SERPAPI_HL=es

GOOGLE_API_KEY=your_google_api_key
```

## Common Commands

Run the local sample scoring demo:

```powershell
python examples/jobfit_demo.py
```

Run the multi-source JobFit flow:

```powershell
python examples/multi_source_jobfit_demo.py
```

Run the focused JobFit test suite:

```powershell
python -m pytest
```

Start the API backend:

```powershell
python start_api.py
```

## Project Layout

```text
.
|-- src/jobfit/
|   |-- scoring.py                    # Job scoring, warnings, location rules
|   `-- agents/
|       |-- adzuna_agent.py           # Adzuna vacancy normalization
|       |-- serpapi_jobs_agent.py     # SerpAPI Google Jobs normalization
|       `-- multi_source_agent.py     # Multi-source search and dedupe
|-- examples/
|   |-- jobfit_demo.py
|   `-- multi_source_jobfit_demo.py
|-- tests/jobfit/
|   |-- test_career_track.py
|   |-- test_dedupe.py
|   |-- test_location_and_red_flags.py
|   `-- test_salary_parsing.py
|-- docs/
|-- config/
`-- output/
```

## Outputs

The multi-source demo writes ranked results to:

- `output/multi_source_jobfit_results.json`
- `output/multi_source_jobfit_results.csv`

Runtime outputs, virtual environments, local databases, and `.env` files are ignored by Git.

## Validation

The main regression checks live under `tests/jobfit` and cover:

- salary parsing and monthly salary normalization
- role and career-track scoring
- ZMVM and Estado de Mexico location behavior
- critical warning detection
- cross-source deduplication and metadata merging

## Repository

- GitHub: https://github.com/CampoyLira1994/JobFit-AI-MVP
- Main branch: `main`
- License: MIT
