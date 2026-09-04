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
    style = read_utf8("references/styles/soft-toy-chibi.md")
    workflow = read_utf8("references/workflows/workflow.md")
    prompt_assembly = read_utf8("references/workflows/prompt-assembly.md")
    quality = read_utf8("references/quality-checklist.md")
    skill = read_utf8("SKILL.md")
    minimal_profile = read_utf8(
        "references/styles/soft-toy-profiles/minimal-face.md"
    )

    require_fragments(
        style,
        [
            "总身高控制在约 2.6～3.3 个头高",
            "超过 3.4 个头高直接失败",
            "外轮廓使用深棕或暖黑粗线",
            "长发可以保留为身份锚点，但必须压缩成 3～7 个清楚的大型发块",
            "精致日系动漫立绘",
            "纯白背景",
            "短而图形化的睫毛",
            "闭眼只作为后续表情",
            "QA 必须与主风格参考图并排查看",
            "prompt_profiles:",
            "soft-toy-profiles/minimal-face.md",
        ],
        "soft-toy-chibi.md",
    )
    require_fragments(
        workflow,
        [
            "生成前缺少 `plan.md` 或对应 Prompt 文件时不得调用图片工具",
            "实际调用同时传入身份图和主风格参考",
            "`qa.md`",
            "失败图保存为失败候选，但不得向用户介绍为“可确认版本”",
            "style-registry.json",
        ],
        "workflow.md",
    )
    require_fragments(
        prompt_assembly,
        [
            "[primary style]",
            "支持多参考图的工具必须把已记录的身份图和风格图真实传入调用",
            "不要压缩成“可爱Q版”",
            "reference_maturity",
        ],
        "prompt-assembly.md",
    )
    require_fragments(
        quality,
        [
            "风格硬门：PASS / FAIL",
            "人物身份层",
            "当前任务层",
            "专属运行契约",
        ],
        "quality-checklist.md",
    )
    require_fragments(
        minimal_profile,
        [
            "参考校准 Prompt",
            "用户生产 Prompt 模板",
            "approximately 2.7–3 head-tall proportions",
            "warm dark-brown outer contours",
            "75%–85% stable flat local colors",
            "Sticker outline: {off by default",
            "Minimal Face 专属 QA",
        ],
        "soft-toy-profiles/minimal-face.md",
    )
    require_fragments(
        skill,
        [
            "风格注册表",
            "图片工具调用必须真实传入",
            "qa.md",
            "失败图不得介绍成可确认版本",
        ],
        "SKILL.md",
    )

    reference_dir = SKILL_ROOT / "assets/style-references/soft-toy-chibi"
    expected_references = {
        "minimal-face-sheet.png",
        "expressive-eye-sheet.png",
        "accessory-led-sheet.png",
        "round-open-eye-sheet.png",
    }
    actual_references = {path.name for path in reference_dir.iterdir() if path.is_file()}
    if actual_references != expected_references:
        raise AssertionError(
            f"软萌潮玩参考图库不完整：expected={sorted(expected_references)}, "
            f"actual={sorted(actual_references)}"
        )

    style_files = {path.name for path in (SKILL_ROOT / "references/styles").glob("*.md")}
    expected_style_files = {
        "soft-toy-chibi.md",
        "streetwear-pixel-sheet.md",
        "charcoal-ink-chibi.md",
    }
    if style_files != expected_style_files:
        raise AssertionError(
            f"当前内置风格定义错误：expected={sorted(expected_style_files)}, "
            f"actual={sorted(style_files)}"
        )

    asset_directories = {
        path.name
        for path in (SKILL_ROOT / "assets/style-references").iterdir()
        if path.is_dir()
    }
    expected_asset_directories = {
        "soft-toy-chibi",
        "streetwear-pixel-sheet",
        "charcoal-ink-chibi",
    }
    if asset_directories != expected_asset_directories:
        raise AssertionError(
            f"当前内置风格资产目录错误：expected={sorted(expected_asset_directories)}, "
            f"actual={sorted(asset_directories)}"
        )

    retired_identifiers = (
        "clean-color-" + "chibi",
        "paper-colored-" + "pencil",
    )
    text_files = [
        path
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"}
    ]
    for text_file in text_files:
        text = text_file.read_text(encoding="utf-8")
        for retired_identifier in retired_identifiers:
            if retired_identifier in text:
                raise AssertionError(
                    f"已删除风格标识仍被引用：{retired_identifier} in {text_file}"
                )

    prompts = json.loads(read_utf8("evals/dev/trigger_cases.json"))
    case_families = {
        case["family"]
        for bucket in ("should_trigger", "should_not_trigger", "near_neighbor")
        for case in prompts[bucket]
    }
    required_cases = {
        "toy_create",
        "formal_photo",
        "toy_turnaround",
        "toy_style_audit",
        "toy_reference_routing",
        "toy_eye_anchor",
        "toy_minimal_profile",
    }
    missing_cases = required_cases - case_families
    if missing_cases:
        raise AssertionError(f"缺少软萌潮玩回归用例：{sorted(missing_cases)}")

    print("validate_soft_toy_contract: PASS")


if __name__ == "__main__":
    main()
