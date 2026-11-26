# Current Architecture and Synchronization Boundary

## Important status note

The public repository currently contains the earlier sanitized JobFit MVP.

The newer canonical local implementation has evolved into Campoy Nexus and has been validated locally, but the full Alpha 1–3A source tree has not yet been synchronized into this public mirror.

This document describes the current validated architecture so collaborators can understand the direction without assuming that every component is already present on `main`.

## Operational architecture

```text
Campoy Nexus Web
        |
        v
     FastAPI
        |
        v
   PostgreSQL
     /   |   \
    /    |    \
profiles runs  results
             /      \
        feedback   saved opportunities
        |
        v
 JobFit Worker
        |
        v
 Job-search provider
```

## Core entities

### Candidate profile

Stores the candidate information used for scoring and routing.

Public examples should be synthetic or sanitized.

### Search run

Represents one execution request.

Expected lifecycle:

```text
queued -> running -> completed
                  -> failed
queued/running -> cancel_requested -> cancelled
```

### Search result

A vacancy evaluated inside one search run.

Each result belongs to a specific `search_run_id`.

### Saved opportunity

A result intentionally promoted into the long-lived opportunity bank.

Search results and saved opportunities are intentionally separate.

## Canonical decision buckets

```text
apply_now
review_requirements
validate_salary
discard
blocked
```

Canonical applicable count:

```text
applicable_count = apply_now_count + review_requirements_count
```

Do not derive applicability from free-text recommendation strings.

## Validated local milestones

### Alpha 1 — Data contract

Implemented and validated locally:

- candidate profiles
- search runs
- search results
- feedback
- saved opportunity relationships
- UUID-based Nexus relationships

### Alpha 2 — Worker pipeline

Implemented and validated locally:

- PostgreSQL-backed queue
- dedicated worker
- real Adzuna execution
- persisted results
- per-run artifacts
- cancellation flow
- canonical counters

A real end-to-end validation completed with:

- 95 raw
- 80 unique
- 10 evaluated/persisted
- 1 apply_now
- 2 review_requirements
- 7 discard
- 3 applicable

This is evidence of one successful execution, not a general quality benchmark.

### Alpha 3A — Web shell

Implemented locally:

- Campoy Nexus navigation
- JobFit summary
- search history
- search-run detail
- results view
- saved opportunities view
- Agents page
- Nexus Lab preserving the legacy control center

The browser-based final visual validation and public synchronization are separate tasks.

## Academic extension: Career Atlas

Career Atlas is not equivalent to the current operational JobFit scoring.

The planned academic layer introduces:

```text
Candidate
   |
   v
Normalized competency (e.g. ESCO)
   |
   v
Traceable evidence
   |
   +--> review state
   +--> reviewer
   +--> source/provenance
   +--> version/date
```

The proposed research compares:

- A: lexical baseline
- B: semantic baseline
- C: semantic ranking adjusted by reviewed evidence

The experiment remains separate from the operational JobFit validation.

## Public synchronization plan

Before declaring this public mirror equivalent to the canonical Nexus implementation:

1. Export only the JobFit/Nexus subset needed for collaboration.
2. Remove private profiles, secrets, artifacts and unrelated modules.
3. Preserve relevant commit/tag provenance where possible.
4. Recreate the API/worker/web structure in a clean public branch.
5. Run tests in the public tree.
6. Review deployment configuration.
7. Deploy only after a public-safe smoke test passes.

Until then, contributors should treat this repository as a **public collaboration mirror**, not the canonical production source.
