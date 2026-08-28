from __future__ import annotations

import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read_utf8(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


def require_fragments(text: str, fragments: list[str], source: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise AssertionError(f"{source} 缺少必要契约：{missing}")


def main() -> None:
    style = read_utf8("references/styles/monochrome-manga-sheet.md")
    skill = read_utf8("SKILL.md")
    auto_selection = read_utf8("references/auto-selection.md")
    prompt_assembly = read_utf8("references/workflows/prompt-assembly.md")
    workflow = read_utf8("references/workflows/workflow.md")
    quality = read_utf8("references/quality-checklist.md")
    palette = read_utf8("references/dimensions/palette.md")

    require_fragments(
        style,
        [
            "reference_maturity: single-reference",
            "default_likeness: recognizable",
            "front_character:",
            "face_hair_detail:",
            "单张候选原则",
            "五项身份指纹",
            "identity_anchor_3_eye_brow_relation",
            "anchor_1_identity_adaptive_eyes",
            "anchor_3_stylized_structure",
            "identity-first",
            "禁止传入图片工具",
            "不默认生成“头像一张＋全身一张”",
        ],
        "monochrome-manga-sheet.md",
    )
    require_fragments(
        skill,
        [
            "极简黑白漫画设定风",
            "monochrome-manga-sheet",
            "`single-reference`",
            "专属运行校验器",
        ],
        "SKILL.md",
    )
    require_fragments(
        auto_selection,
        [
            "纯黑白、漫画线稿成品",
            "用户只说“线稿”但没有说明是否最终成品时，不自动选择",
        ],
        "auto-selection.md",
    )
    require_fragments(
        prompt_assembly,
        [
            "style-registry.json",
            "[primary identity]",
            "[secondary identity]",
            "[primary style]",
            "identity-first",
            "one candidate only",
            "已声明参考图输入顺序的风格严格遵守其定义",
        ],
        "prompt-assembly.md",
    )
    require_fragments(
        workflow,
        [
            "run_validator",
            "reference_maturity",
            "--phase pre",
            "--phase post",
        ],
        "workflow.md",
    )
    require_fragments(
        quality,
        [
            "生成后硬门",
            "负面 QA 样本",
            "风格硬门：PASS / FAIL",
            "运行契约",
            "identity_anchors",
            "不自动生成头像、脸部校准图或第二版",
        ],
        "quality-checklist.md",
    )
    require_fragments(
        palette,
        [
            "`monochrome-manga-sheet`",
            "不保留色相",
        ],
        "palette.md",
    )

    style_reference_dir = SKILL_ROOT / "assets/style-references/monochrome-manga-sheet"
    expected_style_assets = {
        "reference.png",
        "front-character.png",
        "face-hair-detail.png",
    }
    actual_style_assets = {
        path.name for path in style_reference_dir.iterdir() if path.is_file()
    }
    if actual_style_assets != expected_style_assets:
        raise AssertionError(
            f"黑白风格参考资产错误：expected={sorted(expected_style_assets)}, "
            f"actual={sorted(actual_style_assets)}"
        )

    negative_dir = SKILL_ROOT / "assets/qa-negative-examples/monochrome-manga-sheet"
    expected_negative_assets = {
        "generic-anime-head-large.png",
        "generic-anime-body-long.png",
    }
    actual_negative_assets = {
        path.name for path in negative_dir.iterdir() if path.is_file()
    }
    if actual_negative_assets != expected_negative_assets:
        raise AssertionError(
            f"黑白风格负面样本错误：expected={sorted(expected_negative_assets)}, "
            f"actual={sorted(actual_negative_assets)}"
        )

    validator = SKILL_ROOT / "scripts/validate_monochrome_run.py"
    run_contract_reference = (
        SKILL_ROOT / "references/workflows/monochrome-run-contract.md"
    )
    if not validator.is_file() or not run_contract_reference.is_file():
        raise AssertionError("黑白运行契约校验器或说明缺失。")

    validator_text = validator.read_text(encoding="utf-8")
    contract_text = run_contract_reference.read_text(encoding="utf-8")
    require_fragments(
        validator_text,
        [
            'SCHEMA_VERSION = "2.0"',
            "IDENTITY_ANCHOR_IDS",
            "single_candidate_only",
            "identity-first",
            "approved_candidate 要求五项身份锚点和八项风格锚点全部 PASS",
        ],
        "validate_monochrome_run.py",
    )
    require_fragments(
        contract_text,
        [
            '"schema_version": "2.0"',
            '"likeness": "recognizable"',
            '"reference_strategy": "identity-first"',
            '"single_candidate_only": true',
            '"identity_status": "PENDING"',
        ],
        "monochrome-run-contract.md",
    )

    prompts = json.loads(read_utf8("evals/dev/trigger_cases.json"))
    case_families = {
        case["family"]
        for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")
        for case in prompts[bucket]
    }
    required_cases = {
        "mono_create",
        "mono_final_medium",
        "mono_single_reference",
        "mono_turnaround",
        "mono_contamination",
        "mono_generic_anime_failure",
        "mono_reference_order",
    }
    missing_cases = required_cases - case_families
    if missing_cases:
        raise AssertionError(f"缺少极简黑白漫画回归用例：{sorted(missing_cases)}")

    print("validate_monochrome_contract: PASS")


if __name__ == "__main__":
    main()
