#!/usr/bin/env python3
"""校验 Library 包的 UTF-8、JSON、入口预算相关结构和治理元数据。"""

from __future__ import annotations

import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".yaml", ".yml", ".py", ".txt"}


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise AssertionError(f"文本文件不得包含 UTF-8 BOM：{path}")
    return raw.decode("utf-8")


def main() -> None:
    text_files = [
        path
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
    ]
    for path in text_files:
        text = read_utf8(path)
        if path.suffix.lower() == ".json":
            json.loads(text)
        elif path.suffix.lower() == ".jsonl":
            for line_number, line in enumerate(text.splitlines(), start=1):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise AssertionError(f"JSONL 非法：{path}:{line_number}") from exc

    manifest = json.loads(read_utf8(SKILL_ROOT / "manifest.json"))
    if manifest["name"] != "e8-visual-ip":
        raise AssertionError("manifest 与 Skill 身份不一致。")
    if manifest["maturity_tier"] != "library":
        raise AssertionError("当前包必须保持 Library 成熟度。")
    if manifest["asset_distribution"] != "repository-mit-user-confirmed-2026-08-29":
        raise AssertionError("公开资产分发状态必须与仓库所有者确认记录一致。")

    provenance = json.loads(read_utf8(SKILL_ROOT / "assets/provenance.json"))
    if provenance["default_rights_status"] != "owner-confirmed-public-redistribution":
        raise AssertionError("公开资产必须记录所有者再分发确认。")
    if provenance["distribution_policy"] != "repository-mit":
        raise AssertionError("公开资产必须按仓库 MIT 许可证分发。")
    if any(asset["license"] != "MIT" for asset in provenance["assets"]):
        raise AssertionError("存在未采用 MIT 许可证的公开资产。")

    skill_text = read_utf8(SKILL_ROOT / "SKILL.md")
    if "style-registry.json" not in skill_text or "validate_style_registry.py" not in skill_text:
        raise AssertionError("SKILL.md 未路由到风格注册表或校验器。")
    if (SKILL_ROOT / "test-prompts.json").exists():
        raise AssertionError("旧测试格式不得与标准 evals 并存。")

    required_paths = [
        "agents/interface.yaml",
        "agents/openai.yaml",
        "assets/provenance.json",
        "evals/semantic_config.json",
        "reports/output-risk-profile.md",
        "schemas/style.schema.json",
        "security/permission_policy.json",
    ]
    missing = [path for path in required_paths if not (SKILL_ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"Library 包缺少文件：{missing}")

    print(f"test_package_integrity: PASS ({len(text_files)} UTF-8 text files)")


if __name__ == "__main__":
    main()
