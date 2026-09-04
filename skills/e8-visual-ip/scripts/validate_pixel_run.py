#!/usr/bin/env python3
"""校验街头像素正面人物运行在生成前后是否满足硬契约。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "cli"
CONTRACT_NAME = "run-contract.json"
STYLE_ID = "streetwear-pixel-sheet"
SCHEMA_VERSION = "1.0"
ROUTE_FILES = {
    "glasses-cyan": "glasses-cyan.png",
    "long-hair-gold": "long-hair-gold.png",
}
ANCHOR_IDS = (
    "pixel_anchor_1_uniform_grid",
    "pixel_anchor_2_dark_palette",
    "pixel_anchor_3_compact_youth_proportion",
    "pixel_anchor_4_hair_clusters",
    "pixel_anchor_5_simple_face",
    "pixel_anchor_6_streetwear_volume",
    "pixel_anchor_7_single_accent",
    "pixel_anchor_8_clean_fullbody",
)
REQUIRED_KEYS = {
    "schema_version",
    "style_id",
    "task_type",
    "reference_maturity",
    "route",
    "status",
    "identity_references",
    "primary_style_reference",
    "secondary_style_references",
    "reference_order",
    "full_sheet_reference",
    "full_sheet_passed_to_generation",
    "prompt_file",
    "candidate_file",
    "qa_file",
    "out_of_scope",
    "pixel_policy",
    "positive_anchors",
}
PIXEL_POLICY_KEYS = {
    "nearest_neighbor_only",
    "anti_aliasing_forbidden",
    "gradient_forbidden",
    "palette_color_min",
    "palette_color_max",
    "accent_system_count",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("pre", "post"))
    return parser.parse_args()


def read_contract(run_dir: Path) -> dict[str, Any]:
    contract_path = run_dir / CONTRACT_NAME
    if not contract_path.is_file():
        raise FileNotFoundError(f"缺少运行契约：{contract_path}")
    value = json.loads(contract_path.read_text(encoding="utf-8"))
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
    return value


def resolve_existing_file(run_dir: Path, raw_path: str, field: str) -> Path:
    path = Path(raw_path)
    resolved = path if path.is_absolute() else run_dir / path
    resolved = resolved.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"{field} 指向的文件不存在：{resolved}")
    return resolved


def validate_pixel_policy(value: Any) -> None:
    if not isinstance(value, dict):
        raise TypeError("pixel_policy 必须是 JSON 对象。")
    if set(value) != PIXEL_POLICY_KEYS:
        raise ValueError(f"pixel_policy 必须且只能包含：{sorted(PIXEL_POLICY_KEYS)}")
    if value["nearest_neighbor_only"] is not True:
        raise ValueError("nearest_neighbor_only 必须是 true。")
    if value["anti_aliasing_forbidden"] is not True:
        raise ValueError("anti_aliasing_forbidden 必须是 true。")
    if value["gradient_forbidden"] is not True:
        raise ValueError("gradient_forbidden 必须是 true。")
    if value["palette_color_min"] != 16 or value["palette_color_max"] != 28:
        raise ValueError("像素色板目标必须是16～28色。")
    if value["accent_system_count"] != 1:
        raise ValueError("accent_system_count 必须是1。")


def validate_common(run_dir: Path, contract: dict[str, Any]) -> None:
    if contract["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version 必须是 {SCHEMA_VERSION}。")
    if contract["style_id"] != STYLE_ID:
        raise ValueError(f"style_id 必须是 {STYLE_ID}。")
    if contract["task_type"] != "base-character":
        raise ValueError("当前契约只校验首次正面 base-character 运行。")
    if contract["reference_maturity"] != "limited-multi-reference":
        raise ValueError("reference_maturity 必须是 limited-multi-reference。")
    route = require_string(contract["route"], "route")
    if route not in ROUTE_FILES:
        raise ValueError(f"route 必须是：{sorted(ROUTE_FILES)}")
    route_file = ROUTE_FILES[route]

    identities = require_string_list(
        contract["identity_references"], "identity_references", allow_empty=False
    )
    primary = require_string(contract["primary_style_reference"], "primary_style_reference")
    secondary = require_string_list(
        contract["secondary_style_references"],
        "secondary_style_references",
        allow_empty=True,
    )
    reference_order = require_string_list(
        contract["reference_order"], "reference_order", allow_empty=False
    )
    full_sheet = require_string(contract["full_sheet_reference"], "full_sheet_reference")

    if secondary:
        raise ValueError("新像素参考不使用辅助裁图；secondary_style_references 必须为空。")
    if reference_order != [primary, *identities]:
        raise ValueError(
            "reference_order 必须严格为：所选完整像素参考、全部身份图。"
        )
    if Path(primary).name != route_file:
        raise ValueError(f"route={route} 的主参考必须是 {route_file}。")
    if contract["full_sheet_passed_to_generation"] is not True:
        raise ValueError("新参考是完整正面图，必须真实传入生成工具。")

    resolve_existing_file(run_dir, primary, "primary_style_reference")
    for index, identity in enumerate(identities):
        resolve_existing_file(run_dir, identity, f"identity_references[{index}]")
    resolved_sheet = resolve_existing_file(run_dir, full_sheet, "full_sheet_reference")
    if resolved_sheet.name != route_file or resolved_sheet != Path(primary).resolve():
        raise ValueError("full_sheet_reference 必须与当前完整正面主参考相同。")
    resolve_existing_file(
        run_dir,
        require_string(contract["prompt_file"], "prompt_file"),
        "prompt_file",
    )
    require_string_list(contract["out_of_scope"], "out_of_scope", allow_empty=True)
    validate_pixel_policy(contract["pixel_policy"])

    anchors = contract["positive_anchors"]
    if not isinstance(anchors, dict):
        raise TypeError("positive_anchors 必须是 JSON 对象。")
    if set(anchors) != set(ANCHOR_IDS):
        raise ValueError(f"positive_anchors 必须且只能包含：{list(ANCHOR_IDS)}")


def validate_pre(contract: dict[str, Any]) -> None:
    if contract["status"] != "planned":
        raise ValueError("生成前 status 必须是 planned。")
    if contract["candidate_file"] is not None:
        raise ValueError("生成前 candidate_file 必须是 null。")
    if contract["qa_file"] is not None:
        raise ValueError("生成前 qa_file 必须是 null。")
    if any(contract["positive_anchors"][anchor] != "PENDING" for anchor in ANCHOR_IDS):
        raise ValueError("生成前八项 positive_anchors 必须全部是 PENDING。")


def validate_post(run_dir: Path, contract: dict[str, Any]) -> None:
    if contract["status"] not in {"rejected", "approved_candidate"}:
        raise ValueError("生成后 status 必须是 rejected 或 approved_candidate。")
    candidate = require_string(contract["candidate_file"], "candidate_file")
    qa = require_string(contract["qa_file"], "qa_file")
    resolve_existing_file(run_dir, candidate, "candidate_file")
    qa_path = resolve_existing_file(run_dir, qa, "qa_file")

    results = [contract["positive_anchors"][anchor] for anchor in ANCHOR_IDS]
    if any(result not in {"PASS", "FAIL"} for result in results):
        raise ValueError("生成后八项 positive_anchors 只能是 PASS 或 FAIL。")
    if contract["status"] == "approved_candidate" and any(
        result != "PASS" for result in results
    ):
        raise ValueError("approved_candidate 要求八项像素锚点全部 PASS。")
    if contract["status"] == "rejected" and all(result == "PASS" for result in results):
        raise ValueError("rejected 至少需要一项像素锚点为 FAIL。")

    qa_text = qa_path.read_text(encoding="utf-8")
    for anchor in ANCHOR_IDS:
        if anchor not in qa_text:
            raise ValueError(f"qa_file 未记录锚点：{anchor}")


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
    print(f"validate_pixel_run:{arguments.phase}: PASS")


if __name__ == "__main__":
    main()
