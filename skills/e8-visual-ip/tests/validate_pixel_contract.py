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
    style = read_utf8("references/styles/streetwear-pixel-sheet.md")
    skill = read_utf8("SKILL.md")
    auto_selection = read_utf8("references/auto-selection.md")
    prompt_assembly = read_utf8("references/workflows/prompt-assembly.md")
    workflow = read_utf8("references/workflows/workflow.md")
    quality = read_utf8("references/quality-checklist.md")
    palette = read_utf8("references/dimensions/palette.md")
    run_contract = read_utf8("references/workflows/pixel-run-contract.md")

    require_fragments(
        style,
        [
            "display_name: 像素角色设定风",
            "lifecycle_status: active",
            "reference_maturity: limited-multi-reference",
            "default_likeness: interpreted",
            "reference_01:",
            "reference_02:",
            "统一方形像素网格",
            "不定义用户必须具有的发型、眼镜、耳饰、服装、性别或配色",
            "pixel_anchor_6_clothing_blocks",
            "高清插画套马赛克",
        ],
        "streetwear-pixel-sheet.md",
    )
    require_fragments(
        skill,
        [
            "streetwear-pixel-sheet",
            "像素角色设定风",
            "两张合规参考只提供像素画法",
            "专属运行校验器",
        ],
        "SKILL.md",
    )
    require_fragments(
        auto_selection,
        [
            "像素人物、像素三视图",
            "`streetwear-pixel-sheet` 参考使用",
            "不按长短发、眼镜、耳饰、性别或服装自动分流",
        ],
        "auto-selection.md",
    )
    require_fragments(
        run_contract,
        [
            "route` 固定为 `generic-pixel`",
            "不得根据用户的外貌或穿搭拆分路线",
            "发型、眼镜、耳饰、服装和配色必须来自用户照片、文字信息与已确认方案",
        ],
        "pixel-run-contract.md",
    )
    require_fragments(
        prompt_assembly,
        ["style-registry.json", "[primary identity]", "[primary style]", "reference_maturity"],
        "prompt-assembly.md",
    )
    require_fragments(
        workflow,
        ["run_validator", "reference_maturity", "--phase pre", "--phase post"],
        "workflow.md",
    )
    require_fragments(
        quality,
        ["生成后硬门", "负面 QA 样本", "风格硬门：PASS / FAIL", "运行契约"],
        "quality-checklist.md",
    )
    require_fragments(
        palette,
        ["`streetwear-pixel-sheet`", "16～28个有意义颜色"],
        "palette.md",
    )

    reference_dir = SKILL_ROOT / "assets/style-references/streetwear-pixel-sheet"
    expected_assets = {"reference-01.png", "reference-02.png"}
    actual_assets = {path.name for path in reference_dir.iterdir() if path.is_file()}
    if actual_assets != expected_assets:
        raise AssertionError(
            f"像素风格参考资产错误：expected={sorted(expected_assets)}, "
            f"actual={sorted(actual_assets)}"
        )

    validator = SKILL_ROOT / "scripts/validate_pixel_run.py"
    contract_reference = SKILL_ROOT / "references/workflows/pixel-run-contract.md"
    if not validator.is_file() or not contract_reference.is_file():
        raise AssertionError("像素运行契约校验器或说明缺失。")

    prompts = json.loads(read_utf8("evals/dev/trigger_cases.json"))
    case_families = {
        case["family"]
        for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")
        for case in prompts[bucket]
    }
    required_cases = {
        "pixel_create",
        "pixel_reference_isolation",
        "pixel_identity_adaptation",
        "pixel_turnaround",
        "pixel_audit",
        "pixel_contamination",
    }
    missing_cases = required_cases - case_families
    if missing_cases:
        raise AssertionError(f"缺少像素风回归用例：{sorted(missing_cases)}")

    print("validate_pixel_contract: PASS")


if __name__ == "__main__":
    main()
