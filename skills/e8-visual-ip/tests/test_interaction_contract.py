#!/usr/bin/env python3
"""回归测试基础人物、新风格与正式角色衍生的交互关卡。"""

from __future__ import annotations

import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read_utf8(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


def require_fragments(text: str, fragments: list[str], source: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise AssertionError(f"{source} 缺少必要交互契约：{missing}")


def reject_fragments(text: str, fragments: list[str], source: str) -> None:
    present = [fragment for fragment in fragments if fragment in text]
    if present:
        raise AssertionError(f"{source} 仍包含会放宽关卡的旧规则：{present}")


def load_output_cases() -> dict[str, dict[str, object]]:
    cases: dict[str, dict[str, object]] = {}
    source = SKILL_ROOT / "evals/output/cases.jsonl"
    for line_number, line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        case = json.loads(line)
        case_id = case["id"]
        if case_id in cases:
            raise AssertionError(f"输出评测用例 ID 重复：{case_id}，第 {line_number} 行")
        cases[case_id] = case
    return cases


def main() -> None:
    skill = read_utf8("SKILL.md")
    workflow = read_utf8("references/workflows/workflow.md")
    confirmation = read_utf8("references/workflows/confirmation.md")
    partial = read_utf8("references/partial-workflows.md")
    style_catalog = read_utf8("references/style-catalog.md")
    auto_selection = read_utf8("references/auto-selection.md")
    style_presets = read_utf8("references/style-presets.md")

    require_fragments(
        skill,
        [
            "不等于授权立即生图",
            "人物设计方案卡",
            "只生成一张校准样张",
            "不重复人物方案确认而直接执行",
            "禁止静默默认选择任一风格",
        ],
        "SKILL.md",
    )
    require_fragments(
        workflow,
        [
            "第一次响应",
            "输出后必须停下",
            "一张正面校准样张",
            "保持什么，只改变什么",
            "只分析、比较、审计或写方案",
            "首次风格发现",
            "catalog_primary_style",
        ],
        "完整工作流",
    )
    require_fragments(
        confirmation,
        [
            "design_approved",
            "sample_approved",
            "character_confirmed",
            "style_confirmed",
            "catalog_style_selected",
            "它们只是任务意图",
            "校准样张不是正式风格确认",
        ],
        "确认协议",
    )
    require_fragments(
        partial,
        [
            "用户已明确授权按该方案生成",
            "不得把“帮我创建”理解为已授权生图",
            "人物基准和风格均已正式确认",
        ],
        "局部工作流",
    )
    require_fragments(
        style_catalog,
        [
            "真实展示",
            "catalog_preview",
            "catalog_primary_style",
            "采用推荐",
            "还不会开始生成",
            "不得来自另一套人物或画法",
        ],
        "风格目录",
    )
    require_fragments(
        auto_selection + style_presets,
        [
            "不静默选中",
            "不能跳过首次风格目录",
            "选择软萌潮玩后才使用",
        ],
        "自动选择与 Preset",
    )

    reject_fragments(
        skill + workflow + auto_selection + style_presets,
        [
            "默认在烧图前让用户确认",
            "用户明确说“按推荐直接生成”时可以跳过此处",
            "用户只说Q版、个人分身或没有指定风格 | `soft-toy-chibi`",
        ],
        "入口与完整工作流",
    )

    output_cases = load_output_cases()
    required_case_ids = {
        "base-character-pre-generation-gate",
        "custom-style-calibration-gate",
        "confirmed-derivative-fast-path",
        "first-use-style-discovery",
    }
    missing_cases = required_case_ids - set(output_cases)
    if missing_cases:
        raise AssertionError(f"缺少交互回归用例：{sorted(missing_cases)}")

    for case_id in required_case_ids:
        assertions = output_cases[case_id]["assertions"]
        if not isinstance(assertions, list) or len(assertions) < 3:
            raise AssertionError(f"交互用例缺少完整断言：{case_id}")

    print("test_interaction_contract: PASS")


if __name__ == "__main__":
    main()
