#!/usr/bin/env python3
"""校验极简黑白漫画正面人物的身份、风格、参考顺序与单张运行边界。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "cli"
CONTRACT_NAME = "run-contract.json"
STYLE_ID = "monochrome-manga-sheet"
SCHEMA_VERSION = "2.0"
ALLOWED_LIKENESS = {"recognizable", "close", "interpreted"}
IDENTITY_FIRST_LIKENESS = {"recognizable", "close"}
IDENTITY_ANCHOR_IDS = (
    "identity_anchor_1_face_proportion",
    "identity_anchor_2_hairline_forehead",
    "identity_anchor_3_eye_brow_relation",
    "identity_anchor_4_mid_lower_face",
    "identity_anchor_5_age_mood",
)
STYLE_ANCHOR_IDS = (
    "anchor_1_identity_adaptive_eyes",
    "anchor_2_hair_silhouette",
    "anchor_3_stylized_structure",
    "anchor_4_oversized_garment",
    "anchor_5_relaxed_lower_body",
    "anchor_6_line_hierarchy",
    "anchor_7_black_mass",
    "anchor_8_identity_aligned_mood",
)
REQUIRED_KEYS = {
    "schema_version",
    "style_id",
    "task_type",
    "reference_maturity",
    "likeness",
    "reference_strategy",
    "single_candidate_only",
    "status",
    "identity_status",
    "identity_references",
    "primary_style_reference",
    "secondary_style_references",
    "reference_order",
    "full_sheet_reference",
    "full_sheet_passed_to_generation",
    "negative_examples_passed_to_generation",
    "prompt_file",
    "candidate_file",
    "qa_file",
    "out_of_scope",
    "identity_anchors",
    "positive_anchors",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("pre", "post"))
    return parser.parse_args()


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"文本文件不得包含 UTF-8 BOM：{path}")
    return raw.decode("utf-8")


def read_contract(run_dir: Path) -> dict[str, Any]:
    contract_path = run_dir / CONTRACT_NAME
    if not contract_path.is_file():
        raise FileNotFoundError(f"缺少运行契约：{contract_path}")
    value = json.loads(read_utf8(contract_path))
    if not isinstance(value, dict):
        raise TypeError("运行契约必须是 JSON 对象。")
    missing = REQUIRED_KEYS - value.keys()
    if missing:
        raise KeyError(f"运行契约缺少必需字段：{sorted(missing)}")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field} 必须是非空字符串。")
    return value


def require_string_list(value: Any, field: str, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{field} 必须是字符串数组。")
    if not allow_empty and not value:
        raise ValueError(f"{field} 不得为空。")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise TypeError(f"{field} 中的每一项都必须是非空字符串。")
    if len(value) != len(set(value)):
        raise ValueError(f"{field} 不得包含重复路径。")
    return value


def require_anchor_map(value: Any, field: str, expected_ids: tuple[str, ...]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise TypeError(f"{field} 必须是 JSON 对象。")
    if set(value) != set(expected_ids):
        raise ValueError(f"{field} 必须且只能包含：{list(expected_ids)}")
    if not all(isinstance(status, str) for status in value.values()):
        raise TypeError(f"{field} 的状态必须是字符串。")
    return value


def resolve_existing_file(run_dir: Path, raw_path: str, field: str) -> Path:
    path = Path(raw_path)
    resolved = path if path.is_absolute() else run_dir / path
    resolved = resolved.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"{field} 指向的文件不存在：{resolved}")
    return resolved


def expected_reference_order(
    strategy: str,
    identities: list[str],
    primary_style: str,
    secondary_styles: list[str],
) -> list[str]:
    if strategy == "identity-first":
        return [identities[0], primary_style, *identities[1:]]
    if strategy == "style-first":
        return [primary_style, *identities, *secondary_styles]
    raise ValueError("reference_strategy 必须是 identity-first 或 style-first。")


def validate_common(run_dir: Path, contract: dict[str, Any]) -> None:
    if contract["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version 必须是 {SCHEMA_VERSION}。")
    if contract["style_id"] != STYLE_ID:
        raise ValueError(f"style_id 必须是 {STYLE_ID}。")
    if contract["task_type"] != "base-character":
        raise ValueError("当前契约只校验首次正面 base-character 运行。")
    if contract["reference_maturity"] != "single-reference":
        raise ValueError("reference_maturity 必须是 single-reference。")
    if contract["single_candidate_only"] is not True:
        raise ValueError("single_candidate_only 必须是 true；每轮只能生成一张候选。")

    likeness = require_string(contract["likeness"], "likeness")
    if likeness not in ALLOWED_LIKENESS:
        raise ValueError(f"likeness 必须属于：{sorted(ALLOWED_LIKENESS)}")
    strategy = require_string(contract["reference_strategy"], "reference_strategy")
    expected_strategy = "identity-first" if likeness in IDENTITY_FIRST_LIKENESS else "style-first"
    if strategy != expected_strategy:
        raise ValueError(f"likeness={likeness} 必须使用 reference_strategy={expected_strategy}。")

    identities = require_string_list(
        contract["identity_references"], "identity_references", allow_empty=False
    )
    if len(identities) > 2:
        raise ValueError("identity_references 最多两张；必须明确主身份图，不能堆叠全部照片。")
    if strategy == "style-first" and len(identities) != 1:
        raise ValueError("style-first 只允许一张主身份图。")

    primary = require_string(contract["primary_style_reference"], "primary_style_reference")
    if Path(primary).name != "front-character.png":
        raise ValueError("首次正面生成的主风格参考必须是 front-character.png。")
    secondary = require_string_list(
        contract["secondary_style_references"],
        "secondary_style_references",
        allow_empty=True,
    )
    if strategy == "identity-first" and secondary:
        raise ValueError("identity-first 禁止传入辅助脸部风格图；secondary_style_references 必须为空。")
    if len(secondary) > 1:
        raise ValueError("secondary_style_references 最多一张。")
    for path in secondary:
        if Path(path).name != "face-hair-detail.png":
            raise ValueError("当前允许的辅助风格参考仅为 face-hair-detail.png。")

    reference_order = require_string_list(
        contract["reference_order"], "reference_order", allow_empty=False
    )
    expected_order = expected_reference_order(strategy, identities, primary, secondary)
    if reference_order != expected_order:
        raise ValueError(
            f"reference_order 与 {strategy} 契约不一致；expected={expected_order}, actual={reference_order}"
        )
    if strategy == "identity-first" and any(
        Path(path).name == "face-hair-detail.png" for path in reference_order
    ):
        raise ValueError("identity-first 不得把 face-hair-detail.png 传入图片工具。")
    if any(Path(path).name == "reference.png" for path in reference_order):
        raise ValueError("首次正面生成不得把完整三视图 reference.png 传入图片工具。")
    if any("qa-negative-examples" in Path(path).parts for path in reference_order):
        raise ValueError("负面 QA 样本不得出现在图片工具 reference_order 中。")

    if contract["full_sheet_passed_to_generation"] is not False:
        raise ValueError("full_sheet_passed_to_generation 必须是 false。")
    if contract["negative_examples_passed_to_generation"] is not False:
        raise ValueError("负面样本绝对不能传入图片生成工具。")

    for index, identity in enumerate(identities):
        resolve_existing_file(run_dir, identity, f"identity_references[{index}]")
    resolve_existing_file(run_dir, primary, "primary_style_reference")
    for index, style_reference in enumerate(secondary):
        resolve_existing_file(
            run_dir, style_reference, f"secondary_style_references[{index}]"
        )
    resolve_existing_file(
        run_dir,
        require_string(contract["full_sheet_reference"], "full_sheet_reference"),
        "full_sheet_reference",
    )
    resolve_existing_file(
        run_dir,
        require_string(contract["prompt_file"], "prompt_file"),
        "prompt_file",
    )

    require_string_list(contract["out_of_scope"], "out_of_scope", allow_empty=True)
    require_anchor_map(contract["identity_anchors"], "identity_anchors", IDENTITY_ANCHOR_IDS)
    require_anchor_map(contract["positive_anchors"], "positive_anchors", STYLE_ANCHOR_IDS)


def validate_pre(contract: dict[str, Any]) -> None:
    if contract["status"] != "planned":
        raise ValueError("生成前 status 必须是 planned。")
    if contract["identity_status"] != "PENDING":
        raise ValueError("生成前 identity_status 必须是 PENDING。")
    if contract["candidate_file"] is not None:
        raise ValueError("生成前 candidate_file 必须是 null。")
    if contract["qa_file"] is not None:
        raise ValueError("生成前 qa_file 必须是 null。")
    if any(contract["identity_anchors"][anchor] != "PENDING" for anchor in IDENTITY_ANCHOR_IDS):
        raise ValueError("生成前五项 identity_anchors 必须全部是 PENDING。")
    if any(contract["positive_anchors"][anchor] != "PENDING" for anchor in STYLE_ANCHOR_IDS):
        raise ValueError("生成前八项 positive_anchors 必须全部是 PENDING。")


def validate_post(run_dir: Path, contract: dict[str, Any]) -> None:
    if contract["status"] not in {"rejected", "approved_candidate"}:
        raise ValueError("生成后 status 必须是 rejected 或 approved_candidate。")
    if contract["identity_status"] not in {"PASS", "FAIL"}:
        raise ValueError("生成后 identity_status 必须是 PASS 或 FAIL。")

    candidate = require_string(contract["candidate_file"], "candidate_file")
    qa = require_string(contract["qa_file"], "qa_file")
    resolve_existing_file(run_dir, candidate, "candidate_file")
    qa_path = resolve_existing_file(run_dir, qa, "qa_file")

    identity_results = [contract["identity_anchors"][anchor] for anchor in IDENTITY_ANCHOR_IDS]
    style_results = [contract["positive_anchors"][anchor] for anchor in STYLE_ANCHOR_IDS]
    if any(result not in {"PASS", "FAIL"} for result in identity_results):
        raise ValueError("生成后五项 identity_anchors 只能是 PASS 或 FAIL。")
    if any(result not in {"PASS", "FAIL"} for result in style_results):
        raise ValueError("生成后八项 positive_anchors 只能是 PASS 或 FAIL。")

    identity_all_pass = all(result == "PASS" for result in identity_results)
    style_all_pass = all(result == "PASS" for result in style_results)
    expected_identity_status = "PASS" if identity_all_pass else "FAIL"
    if contract["identity_status"] != expected_identity_status:
        raise ValueError(
            "identity_status 与 identity_anchors 不一致；"
            f"expected={expected_identity_status}, actual={contract['identity_status']}"
        )
    if contract["status"] == "approved_candidate" and not (
        identity_all_pass and style_all_pass
    ):
        raise ValueError("approved_candidate 要求五项身份锚点和八项风格锚点全部 PASS。")
    if contract["status"] == "rejected" and identity_all_pass and style_all_pass:
        raise ValueError("身份与风格全部通过时，status 不得是 rejected。")

    qa_text = read_utf8(qa_path)
    for anchor in (*IDENTITY_ANCHOR_IDS, *STYLE_ANCHOR_IDS):
        if anchor not in qa_text:
            raise ValueError(f"qa_file 未记录锚点：{anchor}")
    if f"身份层：{contract['identity_status']}" not in qa_text:
        raise ValueError("qa_file 的身份层状态与 identity_status 不一致。")


def main() -> None:
    arguments = parse_arguments()
    run_dir = arguments.run_dir.resolve()
    if not run_dir.is_dir():
        raise NotADirectoryError(f"运行目录不存在：{run_dir}")
    if not (run_dir / "analysis.md").is_file():
        raise FileNotFoundError("运行目录缺少 analysis.md。")
    if not (run_dir / "plan.md").is_file():
        raise FileNotFoundError("运行目录缺少 plan.md。")

    contract = read_contract(run_dir)
    validate_common(run_dir, contract)
    if arguments.phase == "pre":
        validate_pre(contract)
    else:
        validate_post(run_dir, contract)
    print(f"validate_monochrome_run:{arguments.phase}: PASS")


if __name__ == "__main__":
    main()
