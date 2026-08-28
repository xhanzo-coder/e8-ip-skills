#!/usr/bin/env python3
"""Validate every independently installable Skill in the E8 IP Skills repository."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".yaml", ".yml", ".py", ".txt"}
PUBLIC_SCAN_EXCLUSIONS = {
    "skills/e8-visual-ip/reports/security_trust_report.json",
    "skills/e8-visual-ip/reports/output_quality_scorecard.json",
}
WINDOWS_ABSOLUTE_PATH = re.compile(
    r"(?i)(?:^|[\s\"'`(])(?:[a-z]:[\\/])",
    re.MULTILINE,
)


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM is not allowed: {path}")
    return raw.decode("utf-8")


def validate_json_file(path: Path, text: str) -> None:
    if path.suffix.lower() == ".json":
        json.loads(text)
        return
    if path.suffix.lower() == ".jsonl":
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid JSONL: {path}:{line_number}") from error


def validate_frontmatter(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Missing SKILL.md: {skill_dir}")
    text = read_utf8(skill_md)
    if not text.startswith("---\n"):
        raise ValueError(f"SKILL.md must start with YAML frontmatter: {skill_md}")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise ValueError(f"Unclosed YAML frontmatter: {skill_md}")
    frontmatter = text[4:closing]
    name_match = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter)
    description_match = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
    if name_match is None or description_match is None:
        raise ValueError(f"Frontmatter requires name and description: {skill_md}")
    skill_name = name_match.group(1).strip().strip("\"'")
    if skill_name != skill_dir.name:
        raise ValueError(
            f"Skill directory/name mismatch: directory={skill_dir.name}, name={skill_name}"
        )
    if not description_match.group(1).strip():
        raise ValueError(f"Empty skill description: {skill_md}")


def validate_text_tree() -> int:
    count = 0
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore"}:
            continue
        text = read_utf8(path)
        validate_json_file(path, text)
        relative = path.relative_to(REPO_ROOT).as_posix()
        if relative not in PUBLIC_SCAN_EXCLUSIONS and WINDOWS_ABSOLUTE_PATH.search(text):
            raise ValueError(f"Machine-specific absolute path found: {relative}")
        count += 1
    return count


def run_skill_tests(skill_dir: Path) -> int:
    tests_dir = skill_dir / "tests"
    if not tests_dir.is_dir():
        return 0
    test_files = sorted(
        path
        for path in tests_dir.glob("*.py")
        if path.name.startswith("test_") or path.name.startswith("validate_")
    )
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    for test_file in test_files:
        subprocess.run(
            [sys.executable, str(test_file)],
            cwd=skill_dir,
            env=environment,
            check=True,
        )
    return len(test_files)


def main() -> None:
    if not SKILLS_ROOT.is_dir():
        raise FileNotFoundError(f"Missing skills directory: {SKILLS_ROOT}")
    skill_dirs = sorted(
        path for path in SKILLS_ROOT.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        raise ValueError("No independently installable Skills were found.")

    text_file_count = validate_text_tree()
    test_count = 0
    for skill_dir in skill_dirs:
        validate_frontmatter(skill_dir)
        test_count += run_skill_tests(skill_dir)

    print(
        json.dumps(
            {
                "valid": True,
                "skill_count": len(skill_dirs),
                "text_file_count": text_file_count,
                "executed_test_scripts": test_count,
                "skills": [path.name for path in skill_dirs],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
