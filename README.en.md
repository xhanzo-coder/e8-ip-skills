# E8 IP Skills

An Agent Skills suite for creating and reusing personal visual-IP characters across images, article illustrations, covers, and future media workflows.

> Status: initial open-source release. Workflow and structural tests pass; real visual quality remains explicitly bounded by each style's `unverified_outputs` and quality reports.

[中文](README.md)

## Skills

| Skill | Status | Responsibility |
|---|---|---|
| `e8-visual-ip` | In development | Create, confirm, persist, revise, audit, and reuse a personal visual-IP character |
| `e8-ip-article-illustrator` | Planned | Read a confirmed character package and generate identity-consistent article illustrations |

Every directory under `skills/` must remain independently installable. Skills must not rely on hard-coded sibling paths.

## Installation

After the repository is publicly released, users should be able to install the suite and select only the Skills they need:

```bash
npx skills add xhanzo-coder/e8-ip-skills
```

For project-scoped installation, copy or link one complete Skill directory to:

```text
<project>/.agents/skills/e8-visual-ip/
```

Repository: [github.com/xhanzo-coder/e8-ip-skills](https://github.com/xhanzo-coder/e8-ip-skills)

## Validation

```bash
python scripts/validate_all.py
```

The validator checks package structure, UTF-8 encoding, JSON/JSONL, Skill frontmatter, repository portability, and every bundled Skill regression script.

## Privacy

Do not commit personal photos, `.creator-space/`, character packages, generated outputs, credentials, cookies, API keys, `.env` files, local absolute paths, or runtime caches.

## Release quality rules

- Run real visual regression tests with redistributable fixtures.
- Verify every Skill in an isolated clean installation.

Repository code, Skill text, and the confirmed images listed in the asset provenance manifest are distributed under the [MIT License](LICENSE). See [ASSET_LICENSE.md](ASSET_LICENSE.md).
