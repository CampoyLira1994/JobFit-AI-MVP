# Security and Data Sanitization

JobFit may process candidate and vacancy information. Treat candidate data as
private by default.

## Never commit

- real candidate names used only for testing
- personal email addresses or phone numbers
- home addresses
- CVs, IDs, diplomas or certificates
- API keys, passwords, cookies or tokens
- database URLs containing credentials
- production/local database dumps
- runtime artifacts containing personal data
- private employer or customer information

## Public examples

All committed examples must be synthetic.

The canonical public example identifier is:

```text
Candidate Example 001
```

Use reserved/non-routable example contact data such as:

```text
candidate@example.invalid
```

Do not derive synthetic examples by making small edits to a real person's name
or contact information.

## Environment files

Only `.env.example` may be committed. Real `.env` files are ignored by Git.

Before a push, review:

```bash
git status --short
git diff --check
git diff --cached
```

and verify no secret or personal-data file is staged.

## History caveat

Removing sensitive content in a new commit does not remove it from older Git
objects. If real secrets or sensitive personal data are ever committed, rotate
the secret immediately and rewrite/purge Git history before treating the
repository as sanitized.
