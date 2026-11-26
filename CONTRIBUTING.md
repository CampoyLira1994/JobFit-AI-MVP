# Contributing to JobFit AI

Thanks for reviewing or contributing to JobFit.

This repository is a public collaboration mirror. The canonical local implementation has evolved into Campoy Nexus / JobFit, while this public `main` branch still contains the earlier sanitized MVP. Contributions should therefore be explicit about which layer they affect.

## Before contributing

Please distinguish between:

- **Designed**: architecture or behavior is specified.
- **Implemented**: code exists and is executable.
- **Tested**: the implementation has been exercised and evidence is retained.
- **Validated**: results have been compared against defined objectives or baselines.

Do not describe designed behavior as implemented or validated.

## Good contribution areas

- Search quality
- Deduplication
- Salary normalization
- Location rules
- Explainable scoring
- Decision bucket logic
- Test coverage
- Public-safe example profiles
- Career Atlas competency/evidence modeling
- ESCO mapping experiments
- Evaluation methodology
- Privacy/security review
- UX for reviewing runs and opportunities

## Security rules

Never commit:

- API keys, tokens or credentials
- .env files
- production database URLs
- CVs, IDs or personal documents
- private candidate profiles
- private employer/customer data
- database dumps
- runtime artifacts containing personal data

Use synthetic or explicitly authorized data in tests and examples.

## Suggested workflow

1. Open an issue describing the problem or improvement.
2. Keep changes small and reviewable.
3. Add or update tests when behavior changes.
4. Explain expected behavior and how you validated it.
5. Avoid unrelated refactors in the same pull request.
6. Do not change scoring semantics silently.
7. Document any new provider assumptions or data-use restrictions.

## Academic boundary

JobFit is a technical antecedent for the JobFit + Career Atlas academic proposal.

The research contribution is **not** the existing search pipeline by itself. The proposed academic work concerns traceable evidence linked to competencies and comparison of lexical, semantic and evidence-adjusted ranking approaches.

Do not claim that the current system:

- authenticates degrees or certificates;
- proves professional competence;
- has validated the Career Atlas evidence model;
- has already completed the A/B/C experiment;
- has demonstrated improvements in NDCG@5 or Precision@5.

Those claims require separate evidence.

## Pull request checklist

- [ ] No secrets or personal data included.
- [ ] Scope is clear.
- [ ] Behavior is described as designed / implemented / tested / validated accurately.
- [ ] Tests added or updated when applicable.
- [ ] No unrelated files changed.
- [ ] Any external API or data-source terms are respected.
- [ ] README/docs updated if architecture or behavior changes.
