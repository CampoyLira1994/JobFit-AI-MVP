# JobFit AI — public collaboration mirror

JobFit is a job-discovery and decision-support project that searches vacancies, normalizes and deduplicates results, evaluates fit against a candidate profile, and separates **search results** from **opportunities intentionally saved for follow-up**.

> **Repository status (November 2026):** this public repository still contains the original sanitized MVP snapshot. The canonical local implementation has advanced into **Campoy Nexus / JobFit** with a PostgreSQL-backed execution model, a dedicated worker and a web interface. That newer source has **not yet been synchronized into this public mirror**, so contributors should not assume every capability described below is already present on `main`.

## Why the project exists

Job boards return many vacancies, but finding a vacancy is not the same as deciding whether it is worth applying to. JobFit is designed to make that second step explicit and auditable.

The intended flow is:

```text
Candidate profile
      ↓
Search preset
      ↓
Job provider (currently Adzuna in the validated Nexus flow)
      ↓
Normalize + deduplicate
      ↓
Filter + score
      ↓
Decision bucket
      ↓
Manual review
      ↓
Saved opportunity / application tracking
```

JobFit does **not** automatically apply to jobs and it must not invent degrees, licenses, certifications, tools or experience that are not supported by the candidate profile.

## Current validated architecture

The newer Campoy Nexus implementation has been validated locally with the following separation:

```text
Campoy Nexus Web
      ↓
FastAPI
      ↓
PostgreSQL
      ├── candidate profiles
      ├── search runs
      ├── search results
      ├── feedback
      └── saved opportunities
      ↓
JobFit Worker
      ↓
Job-search provider
```

A search run follows an explicit lifecycle such as:

```text
queued → running → completed
```

and results are classified into canonical decision buckets:

- `apply_now`
- `review_requirements`
- `validate_salary`
- `discard`
- `blocked`

The saved-opportunity bank is intentionally separate from raw search results. A result should only become a tracked opportunity after an explicit save action.

## Validated milestones

The canonical local project has reached these milestones:

- **Alpha 1 — data contract:** candidate profiles, search runs, search results, feedback and saved-opportunity relationships.
- **Alpha 2 — real worker pipeline:** PostgreSQL queue, dedicated JobFit worker, real Adzuna execution, persisted results and per-run artifacts.
- **Alpha 3A — Nexus web shell:** navigation and read-only JobFit views for search history, run details, results and saved opportunities.

One real end-to-end validation run completed with:

- 95 raw results
- 80 unique results
- 10 evaluated/persisted results
- 1 `apply_now`
- 2 `review_requirements`
- 7 `discard`
- 3 canonical applicable results

These figures document one validation execution; they are **not** claims about general model quality.

## Academic extension: JobFit + Career Atlas

The project is also being used as a technical antecedent for an academic innovation proposal.

The distinction is important:

### Existing technical antecedent

JobFit / Campoy Nexus provides search, execution, persistence, scoring infrastructure, operational traceability and the opportunity workflow.

### Research contribution still to be tested

Career Atlas proposes adding traceable, human-reviewed evidence linked to normalized competencies and comparing:

- **A:** lexical baseline
- **B:** semantic baseline
- **C:** semantic ranking adjusted with reviewed evidence

The academic hypothesis is not considered validated until the planned dataset, annotation, baselines, metrics and A/B/C experiment are actually executed.

No claim is made that JobFit authenticates degrees, certificates or professional competence.

## What is currently in this public repository

The current `main` branch is the earlier sanitized Python MVP. It includes:

- JobFit scoring logic
- Adzuna / SerpAPI-oriented search components
- examples and tests
- an older FastAPI service
- Docker support
- deployment documentation

It does **not yet contain the complete Campoy Nexus Alpha 1–3A source tree** described above.

This status is intentional to avoid publishing local secrets, personal candidate data, runtime artifacts or unrelated Campoy Agent Core modules before a controlled public synchronization.

## Collaboration priorities

Contributions are especially useful in these areas:

1. Search quality and deduplication.
2. Explainable scoring and decision buckets.
3. Salary normalization and location rules.
4. Public-safe candidate profile schemas.
5. Test coverage and reproducibility.
6. Career Atlas competency/evidence data model.
7. ESCO mapping experiments.
8. Evaluation methodology: NDCG@5, Precision@5 and explanation fidelity.
9. Security/privacy review before public deployment.
10. Web UX for reviewing search runs and opportunities.

See [CONTRIBUTING.md](CONTRIBUTING.md) for collaboration rules and [docs/CURRENT_ARCHITECTURE.md](docs/CURRENT_ARCHITECTURE.md) for the target architecture and synchronization boundary.

## Security and privacy

Never commit:

- `.env` files
- API keys or tokens
- database URLs containing credentials
- CVs or identity documents
- private candidate profiles
- private company/customer information
- runtime artifacts with personal data
- production database dumps

Use synthetic or explicitly authorized data in examples and tests.

## Running the current public MVP

The commands below apply to the code that is currently published on `main`:

```powershell
git clone https://github.com/CampoyLira1994/JobFit-AI-MVP.git
cd JobFit-AI-MVP

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest
```

Create a local `.env` from `.env.example` and only configure providers you are authorized to use.

## Deployment status

The Cloud Run workflow currently present in the repository belongs to the older MVP and its historical runs failed. It should **not be treated as a live deployment of Campoy Nexus**.

A new public deployment should only be enabled after:

1. the sanitized Nexus subset is synchronized;
2. deployment configuration is updated to the current architecture;
3. required cloud secrets are configured;
4. API, database and worker boundaries are reviewed for public exposure;
5. a smoke test passes against the deployed environment.

## Repository

- Public mirror: https://github.com/CampoyLira1994/JobFit-AI-MVP
- Default branch: `main`
- License: MIT

Issues and pull requests are welcome. When proposing changes, distinguish clearly between **designed**, **implemented**, **tested** and **validated** behavior.
