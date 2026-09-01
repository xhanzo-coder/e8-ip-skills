#!/usr/bin/env python3
"""Validate one mint-ink-chibi candidate calibration run before and after generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
STYLE_ID = "mint-ink-chibi"
IDENTITY_ANCHOR_IDS = (
    "identity_face_proportion",
    "identity_hairline_silhouette",
    "identity_eye_brow_relation",
    "identity_lower_face_relation",
    "identity_age_mood",
)
STYLE_ANCHOR_IDS = (
    "mint_anchor_1_compact_ratio",
    "mint_anchor_2_head_limb_contrast",
    "mint_anchor_3_forest_line_hierarchy",
    "mint_anchor_4_three_color_limit",
    "mint_anchor_5_negative_space_hair",
    "mint_anchor_6_minimal_face",
    "mint_anchor_7_large_garment_blocks",
    "mint_anchor_8_clean_presentation",
)
PROMPT_CONTRACT_KEYS = {
    "compact_ratio",
    "forest_line_hierarchy",
    "three_color_limit",
    "negative_space_hair",
    "minimal_face_grammar",
    "large_garment_blocks",
    "no_shading_or_texture",
    "reference_content_isolation",
}
REQUIRED_FIELDS = {
    "schema_version",
    "style_id",
    "lifecycle_status",
    "task",
    "reference_maturity",
    "transformation_policy",
    "likeness",
    "single_candidate_only",
    "identity_references",
    "primary_style_reference",
    "reference_order",
    "full_sheet_passed_to_generation",
    "negative_examples_passed_to_generation",
    "prompt_file",
    "prompt_contract",
    "out_of_scope",
    "identity_anchors",
    "style_anchors",
    "identity_status",
    "style_status",
    "task_status",
    "status",
    "candidate_file",
    "qa_file",
}


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"文本文件不得包含 UTF-8 BOM：{path}")
    return raw.decode("utf-8")


def resolve_file(run_dir: Path, value: str, field: str) -> Path:
    path = Path(value)
    resolved = path if path.is_absolute() else run_dir / path
    if not resolved.is_file():
        raise FileNotFoundError(f"{field} 指向的文件不存在：{resolved}")
    return resolved


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field} 必须为非空字符串。")
    return value


def require_string_list(value: Any, field: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{field} 必须为字符串数组。")
    if not allow_empty and not value:
        raise ValueError(f"{field} 不得为空。")
    if any(not isinstance(item, str) or not item for item in value):
        raise TypeError(f"{field} 只能包含非空字符串。")
    if len(value) != len(set(value)):
        raise ValueError(f"{field} 不得包含重复项。")
    return value


def require_status_map(value: Any, field: str, expected_ids: tuple[str, ...]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise TypeError(f"{field} 必须为对象。")
    if set(value) != set(expected_ids):
        raise ValueError(f"{field} 必须且只能包含：{list(expected_ids)}")
    if any(not isinstance(status, str) for status in value.values()):
        raise TypeError(f"{field} 状态必须为字符串。")
    return value


def read_contract(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "run-contract.json"
    if not path.is_file():
        raise FileNotFoundError(f"缺少运行契约：{path}")
    value = json.loads(read_utf8(path))
    if not isinstance(value, dict):
        raise TypeError("运行契约必须为 JSON 对象。")
    missing = REQUIRED_FIELDS - set(value)
    if missing:
        raise KeyError(f"运行契约缺少字段：{sorted(missing)}")
    return value


def validate_common(run_dir: Path, contract: dict[str, Any]) -> None:
    if contract["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version 必须为 {SCHEMA_VERSION}。")
    if contract["style_id"] != STYLE_ID:
        raise ValueError(f"style_id 必须为 {STYLE_ID}。")
    if contract["lifecycle_status"] != "candidate":
        raise ValueError("薄荷墨线校准期间 lifecycle_status 必须为 candidate。")
    if contract["task"] != "base-character":
        raise ValueError("当前契约只允许首次正面 base-character 校准。")
    if contract["reference_maturity"] != "single-reference":
        raise ValueError("reference_maturity 必须为 single-reference。")
    if contract["transformation_policy"] != "structural-redraw":
        raise ValueError("transformation_policy 必须为 structural-redraw。")
    if contract["likeness"] not in {"interpreted", "recognizable"}:
        raise ValueError("候选校准只允许 interpreted 或 recognizable。")
    if contract["single_candidate_only"] is not True:
        raise ValueError("single_candidate_only 必须为 true。")

    identities = require_string_list(
        contract["identity_references"],
        "identity_references",
        allow_empty=False,
    )
    if len(identities) > 2:
        raise ValueError("identity_references 最多两张，避免稀释身份。")
    for index, identity in enumerate(identities):
        resolve_file(run_dir, identity, f"identity_references[{index}]")

    primary = require_string(contract["primary_style_reference"], "primary_style_reference")
    primary_path = resolve_file(run_dir, primary, "primary_style_reference")
    if primary_path.name != "reference.png" or "mint-ink-chibi" not in primary_path.parts:
        raise ValueError("主风格参考必须是登记的 mint-ink-chibi/reference.png。")

    reference_order = require_string_list(
        contract["reference_order"],
        "reference_order",
        allow_empty=False,
    )
    expected_order = [primary, *identities]
    if reference_order != expected_order:
        raise ValueError(
            f"reference_order 必须为主风格在前、身份图在后：expected={expected_order}"
        )
    if contract["full_sheet_passed_to_generation"] is not True:
        raise ValueError("当前单参考候选必须真实传入完整 reference.png。")
    if contract["negative_examples_passed_to_generation"] is not False:
        raise ValueError("负面 QA 样本不得传入图片工具。")

    prompt_file = require_string(contract["prompt_file"], "prompt_file")
    resolve_file(run_dir, prompt_file, "prompt_file")
    prompt_contract = contract["prompt_contract"]
    if not isinstance(prompt_contract, dict) or set(prompt_contract) != PROMPT_CONTRACT_KEYS:
        raise ValueError(f"prompt_contract 必须且只能包含：{sorted(PROMPT_CONTRACT_KEYS)}")
    if any(value is not True for value in prompt_contract.values()):
        raise ValueError("prompt_contract 的八项风格约束必须全部为 true。")

    require_string_list(contract["out_of_scope"], "out_of_scope", allow_empty=True)
    require_status_map(contract["identity_anchors"], "identity_anchors", IDENTITY_ANCHOR_IDS)
    require_status_map(contract["style_anchors"], "style_anchors", STYLE_ANCHOR_IDS)


def validate_pre(contract: dict[str, Any]) -> None:
    if contract["status"] != "planned":
        raise ValueError("生成前 status 必须为 planned。")
    for field in ("identity_status", "style_status", "task_status"):
        if contract[field] != "PENDING":
            raise ValueError(f"生成前 {field} 必须为 PENDING。")
    if contract["candidate_file"] is not None or contract["qa_file"] is not None:
        raise ValueError("生成前 candidate_file 和 qa_file 必须为 null。")
    if any(status != "PENDING" for status in contract["identity_anchors"].values()):
        raise ValueError("生成前身份锚点必须全部为 PENDING。")
    if any(status != "PENDING" for status in contract["style_anchors"].values()):
        raise ValueError("生成前风格锚点必须全部为 PENDING。")


def validate_post(run_dir: Path, contract: dict[str, Any]) -> None:
    if contract["status"] not in {"rejected", "approved_candidate"}:
        raise ValueError("生成后 status 必须为 rejected 或 approved_candidate。")
    for field in ("identity_status", "style_status", "task_status"):
        if contract[field] not in {"PASS", "FAIL"}:
            raise ValueError(f"生成后 {field} 必须为 PASS 或 FAIL。")

    identity_results = list(contract["identity_anchors"].values())
    style_results = list(contract["style_anchors"].values())
    if any(status not in {"PASS", "FAIL"} for status in identity_results):
        raise ValueError("生成后身份锚点只能为 PASS 或 FAIL。")
    if any(status not in {"PASS", "FAIL"} for status in style_results):
        raise ValueError("生成后风格锚点只能为 PASS 或 FAIL。")

    identity_required = 5 if contract["likeness"] == "recognizable" else 3
    identity_pass = sum(status == "PASS" for status in identity_results) >= identity_required
    style_pass = all(status == "PASS" for status in style_results)
    expected_identity = "PASS" if identity_pass else "FAIL"
    expected_style = "PASS" if style_pass else "FAIL"
    if contract["identity_status"] != expected_identity:
        raise ValueError("identity_status 与身份锚点通过数量不一致。")
    if contract["style_status"] != expected_style:
        raise ValueError("style_status 与八项风格锚点不一致。")

    all_pass = identity_pass and style_pass and contract["task_status"] == "PASS"
    expected_status = "approved_candidate" if all_pass else "rejected"
    if contract["status"] != expected_status:
        raise ValueError(f"最终状态错误：expected={expected_status}, actual={contract['status']}")

    candidate = resolve_file(
        run_dir,
        require_string(contract["candidate_file"], "candidate_file"),
        "candidate_file",
    )
    qa = resolve_file(
        run_dir,
        require_string(contract["qa_file"], "qa_file"),
        "qa_file",
    )
    if candidate.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("candidate_file 必须为栅格图片。")
    qa_text = read_utf8(qa)
    for anchor in (*IDENTITY_ANCHOR_IDS, *STYLE_ANCHOR_IDS):
        if anchor not in qa_text:
            raise ValueError(f"qa_file 未记录锚点：{anchor}")
    for label, field in (
        ("身份层", "identity_status"),
        ("风格层", "style_status"),
        ("任务层", "task_status"),
    ):
        if f"{label}：{contract[field]}" not in qa_text:
            raise ValueError(f"qa_file 的{label}与运行契约不一致。")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验薄荷墨线候选正面人物运行。")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--phase", choices=("pre", "post"), required=True)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    run_dir = arguments.run_dir.resolve()
    if not run_dir.is_dir():
        raise NotADirectoryError(f"运行目录不存在：{run_dir}")
    for required in ("analysis.md", "plan.md"):
        if not (run_dir / required).is_file():
            raise FileNotFoundError(f"运行目录缺少 {required}。")
    contract = read_contract(run_dir)
    validate_common(run_dir, contract)
    if arguments.phase == "pre":
        validate_pre(contract)
    else:
        validate_post(run_dir, contract)
    print(f"validate_mint_ink_run:{arguments.phase}: PASS")


if __name__ == "__main__":
    main()
