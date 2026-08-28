# Contributing

This repository is not open for public distribution yet. These rules define the intended contribution boundary for local and future public work.

## Principles

- Keep every `skills/<name>/` directory independently installable.
- Do not introduce hard-coded sibling Skill paths.
- Keep identity data separate from style references.
- Do not weaken confirmation, privacy, or output-boundary gates to make a demo pass.
- Add regression coverage for every confirmed failure.

## Visual assets

Every added image must include provenance, rights status, source class, and SHA-256 metadata. Do not add scraped artwork, user portraits, screenshots with personal information, or generated images whose redistribution terms are unknown.

## Tests

Run before submitting changes:

```bash
python scripts/validate_all.py
```

Visual-output changes also require a human comparison against the declared identity and style references. Text assertions alone are insufficient.

## Pull requests

Describe:

- the affected Skill;
- the observed failure or requested behavior;
- files and outputs changed;
- tests executed;
- remaining unverified behavior;
- asset provenance when images are involved.
