#!/usr/bin/env python3
"""校验 E8 视觉 IP 内置风格注册表、定义文件和资产引用。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "cli"
REQUIRED_FIELDS = {
    "schema_version",
    "id",
    "display_name",
    "aliases",
    "catalog_preview",
    "catalog_primary_style",
    "catalog_summary",
    "catalog_best_for",
    "transformation_policy",
    "reference_maturity",
    "default_likeness",
    "definition",
    "reference_assets",
    "negative_examples",
    "supported_outputs",
    "unverified_outputs",
    "run_validator",
    "prompt_profiles",
}
ALLOWED_TRANSFORMATION_POLICIES = {"surface-mapping", "structural-redraw"}
ALLOWED_REFERENCE_MATURITY = {
    "single-reference",
    "limited-multi-reference",
    "multi-reference",
}
ALLOWED_LIKENESS = {"symbolic", "interpreted", "recognizable", "close"}
ALLOWED_OUTPUTS = {
    "base-character",
    "turnaround",
    "avatar",
    "expression",
    "action",
    "sticker",
    "outfit",
    "scene",
}
STYLE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"文本文件不得包含 UTF-8 BOM：{path}")
    return raw.decode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_utf8(path))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 根节点必须是对象：{path}")
    return value


def frontmatter_scalar(text: str, field: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("风格定义缺少 YAML frontmatter。")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise ValueError("风格定义的 YAML frontmatter 未闭合。")
    frontmatter = text[4:closing]
    match = re.search(rf"(?m)^{re.escape(field)}:\s*([^\n]+)$", frontmatter)
    if match is None:
        raise ValueError(f"风格定义 frontmatter 缺少字段：{field}")
    return match.group(1).strip().strip('"\'')


def require_string_list(entry: dict[str, Any], field: str, *, allow_empty: bool) -> list[str]:
    value = entry[field]
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise TypeError(f"{entry['id']}.{field} 必须是非空字符串数组。")
    if not allow_empty and not value:
        raise ValueError(f"{entry['id']}.{field} 不得为空。")
    if len(value) != len(set(value)):
        raise ValueError(f"{entry['id']}.{field} 不得包含重复值。")
    return value


def validate_entry(skill_root: Path, entry: dict[str, Any]) -> dict[str, int | str]:
    missing = REQUIRED_FIELDS - set(entry)
    if missing:
        raise ValueError(f"风格注册项缺少字段：{sorted(missing)}")

    style_id = entry["id"]
    if not isinstance(style_id, str) or STYLE_ID_PATTERN.fullmatch(style_id) is None:
        raise ValueError(f"非法风格 id：{style_id!r}")
    if entry["schema_version"] != "1.1":
        raise ValueError(f"{style_id} 的 schema_version 必须为 1.1。")
    if entry["transformation_policy"] not in ALLOWED_TRANSFORMATION_POLICIES:
        raise ValueError(f"{style_id} 的 transformation_policy 非法。")
    if entry["reference_maturity"] not in ALLOWED_REFERENCE_MATURITY:
        raise ValueError(f"{style_id} 的 reference_maturity 非法。")
    if entry["default_likeness"] not in ALLOWED_LIKENESS:
        raise ValueError(f"{style_id} 的 default_likeness 非法。")

    aliases = require_string_list(entry, "aliases", allow_empty=False)
    catalog_best_for = require_string_list(entry, "catalog_best_for", allow_empty=False)
    reference_assets = require_string_list(entry, "reference_assets", allow_empty=False)
    negative_examples = require_string_list(entry, "negative_examples", allow_empty=True)
    supported_outputs = require_string_list(entry, "supported_outputs", allow_empty=False)
    unverified_outputs = require_string_list(entry, "unverified_outputs", allow_empty=True)
    prompt_profiles = require_string_list(entry, "prompt_profiles", allow_empty=True)

    catalog_preview = entry["catalog_preview"]
    if not isinstance(catalog_preview, str) or not catalog_preview:
        raise TypeError(f"{style_id}.catalog_preview 必须为非空字符串。")
    if catalog_preview not in reference_assets:
        raise ValueError(f"{style_id}.catalog_preview 必须同时登记在 reference_assets。")
    catalog_primary_style = entry["catalog_primary_style"]
    if not isinstance(catalog_primary_style, str) or not catalog_primary_style:
        raise TypeError(f"{style_id}.catalog_primary_style 必须为非空字符串。")
    if catalog_primary_style not in reference_assets:
        raise ValueError(f"{style_id}.catalog_primary_style 必须同时登记在 reference_assets。")
    catalog_summary = entry["catalog_summary"]
    if not isinstance(catalog_summary, str) or not catalog_summary.strip():
        raise TypeError(f"{style_id}.catalog_summary 必须为非空字符串。")

    unknown_outputs = (set(supported_outputs) | set(unverified_outputs)) - ALLOWED_OUTPUTS
    if unknown_outputs:
        raise ValueError(f"{style_id} 包含未知交付类型：{sorted(unknown_outputs)}")
    overlap = set(supported_outputs) & set(unverified_outputs)
    if overlap:
        raise ValueError(f"{style_id} 的已支持与未验证产物重叠：{sorted(overlap)}")

    definition = skill_root / entry["definition"]
    if not definition.is_file():
        raise FileNotFoundError(f"风格定义不存在：{definition}")
    definition_text = read_utf8(definition)
    expected_scalars = {
        "id": style_id,
        "display_name": entry["display_name"],
        "transformation_policy": entry["transformation_policy"],
        "reference_maturity": entry["reference_maturity"],
        "default_likeness": entry["default_likeness"],
    }
    for field, expected in expected_scalars.items():
        actual = frontmatter_scalar(definition_text, field)
        if actual != expected:
            raise ValueError(
                f"{style_id} 的注册表与定义不一致：{field} expected={expected!r}, actual={actual!r}"
            )

    referenced_paths = [catalog_preview, catalog_primary_style, *reference_assets, *negative_examples, *prompt_profiles]
    for relative_path in referenced_paths:
        path = skill_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"{style_id} 引用的文件不存在：{path}")

    run_validator = entry["run_validator"]
    if run_validator is not None:
        if not isinstance(run_validator, str) or not (skill_root / run_validator).is_file():
            raise FileNotFoundError(f"{style_id} 的运行校验器不存在：{run_validator}")

    return {
        "id": style_id,
        "alias_count": len(aliases),
        "catalog_preview": catalog_preview,
        "catalog_primary_style": catalog_primary_style,
        "catalog_best_for_count": len(catalog_best_for),
        "reference_asset_count": len(reference_assets),
        "supported_output_count": len(supported_outputs),
    }


def validate_registry(skill_root: Path) -> dict[str, Any]:
    registry_path = skill_root / "references" / "style-registry.json"
    registry = load_json(registry_path)
    if registry["schema_version"] != "1.1":
        raise ValueError("style-registry.json 的 schema_version 必须为 1.1。")
    styles = registry["styles"]
    if not isinstance(styles, list) or not styles:
        raise ValueError("style-registry.json.styles 必须是非空数组。")

    results = [validate_entry(skill_root, entry) for entry in styles]
    style_ids = [result["id"] for result in results]
    if len(style_ids) != len(set(style_ids)):
        raise ValueError("风格注册表包含重复 id。")

    registered_definitions = {Path(entry["definition"]).name for entry in styles}
    actual_definitions = {path.name for path in (skill_root / "references" / "styles").glob("*.md")}
    if registered_definitions != actual_definitions:
        raise ValueError(
            "风格定义与注册表不一致："
            f"registered={sorted(registered_definitions)}, actual={sorted(actual_definitions)}"
        )

    registered_assets = {
        path
        for entry in styles
        for path in [*entry["reference_assets"], *entry["negative_examples"]]
    }
    actual_assets = {
        path.relative_to(skill_root).as_posix()
        for root in (
            skill_root / "assets" / "style-references",
            skill_root / "assets" / "qa-negative-examples",
        )
        if root.exists()
        for path in root.rglob("*")
        if path.is_file()
    }
    if registered_assets != actual_assets:
        raise ValueError(
            "风格资产与注册表不一致："
            f"missing={sorted(actual_assets - registered_assets)}, "
            f"unknown={sorted(registered_assets - actual_assets)}"
        )

    provenance = load_json(skill_root / "assets" / "provenance.json")
    if provenance["schema_version"] != "1.1":
        raise ValueError("assets/provenance.json 的 schema_version 必须为 1.1。")
    if provenance["default_rights_status"] != "owner-confirmed-public-redistribution":
        raise ValueError("公开仓库资产必须记录 owner-confirmed-public-redistribution。")
    if provenance["distribution_policy"] != "repository-mit":
        raise ValueError("公开仓库资产必须使用 repository-mit 分发策略。")
    provenance_entries = provenance["assets"]
    if not isinstance(provenance_entries, list):
        raise TypeError("assets/provenance.json.assets 必须是数组。")
    provenance_by_path = {entry["path"]: entry for entry in provenance_entries}
    if len(provenance_by_path) != len(provenance_entries):
        raise ValueError("assets/provenance.json 包含重复路径。")
    if set(provenance_by_path) != actual_assets:
        raise ValueError(
            "资产来源清单与实际资产不一致："
            f"missing={sorted(actual_assets - set(provenance_by_path))}, "
            f"unknown={sorted(set(provenance_by_path) - actual_assets)}"
        )
    for relative_path, entry in provenance_by_path.items():
        if entry["license"] != "MIT":
            raise ValueError(f"公开资产许可证必须为 MIT：{relative_path}")
        if entry["confirmed_by"] != "xhanzo-coder":
            raise ValueError(f"公开资产缺少确认人：{relative_path}")
        if entry["confirmed_at"] != "2026-08-29":
            raise ValueError(f"公开资产确认日期错误：{relative_path}")
        expected_rights = (
            "inherited-public-redistribution"
            if entry["role"] == "derived_crop"
            else "owner-confirmed-public-redistribution"
        )
        if entry["rights_status"] != expected_rights:
            raise ValueError(f"公开资产权属状态错误：{relative_path}")
        observed_hash = hashlib.sha256((skill_root / relative_path).read_bytes()).hexdigest()
        if entry["sha256"] != observed_hash:
            raise ValueError(f"资产哈希不一致：{relative_path}")
        if entry["role"] == "derived_crop":
            source = entry["derived_from"]
            if source not in provenance_by_path:
                raise ValueError(f"衍生资产缺少来源记录：{relative_path} -> {source}")

    for style in styles:
        catalog_preview = style["catalog_preview"]
        catalog_primary_style = style["catalog_primary_style"]
        if catalog_primary_style == catalog_preview:
            continue
        primary_provenance = provenance_by_path[catalog_primary_style]
        if primary_provenance["role"] != "derived_crop":
            raise ValueError(
                f"{style['id']}.catalog_primary_style 与目录预览不同时必须是 derived_crop。"
            )
        if primary_provenance["derived_from"] != catalog_preview:
            raise ValueError(
                f"{style['id']}.catalog_primary_style 必须直接衍生自 catalog_preview。"
            )

    return {
        "valid": True,
        "style_count": len(results),
        "asset_count": len(actual_assets),
        "styles": results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验 E8 视觉 IP 风格注册表。")
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skill 根目录；默认使用脚本所在的 e8-visual-ip。",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = validate_registry(args.skill_dir.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
