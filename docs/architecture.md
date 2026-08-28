# Architecture

## Repository model

`e8-ip-skills` is a suite repository. Each Skill owns one user job and remains independently installable.

```text
skills/e8-visual-ip
    writes confirmed character packages

skills/e8-ip-article-illustrator
    reads character packages and generates article illustrations
```

## Character-package ownership

`e8-visual-ip` is the only Skill allowed to create or update the formal character package:

```text
.creator-space/visual-ip/characters/<character-key>/
```

Downstream Skills may read:

- confirmed identity anchors;
- the selected style definition;
- confirmed reference images;
- allowed variations and forbidden drift.

They must not silently update the package. If a downstream task reveals a needed character change, it returns a change proposal to `e8-visual-ip`.

## Standalone behavior

An article-illustration Skill must also work without `.creator-space` by accepting a user-provided confirmed character image. It must label identity consistency as limited when no formal package exists.

## Shared code

Do not create a shared runtime package until at least two Skills repeat the same deterministic implementation. When shared code is introduced, every released Skill must still bundle or resolve everything required for standalone installation. CI must detect drift between the shared source and bundled copies.

## Release model

- Repository versioning uses SemVer tags.
- Each Skill also keeps its own manifest version.
- A release must identify exactly which Skill versions changed.
- Public release artifacts exclude personal fixtures, local state, unlicensed images, and machine-specific reports.
