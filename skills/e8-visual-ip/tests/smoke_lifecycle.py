#!/usr/bin/env python3
"""离线测试角色包创建、自定义风格扩展、解析、备份和自动创建 creator-space。"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT = SKILL_DIR / "scripts" / "character_pack.py"
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z4QAAAABJRU5ErkJggg=="
)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def write_image(path: Path, suffix: bytes = b"") -> None:
    path.write_bytes(PNG_1X1 + suffix)


def run_json(*arguments: str, expect_success: bool = True) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    if not expect_success:
        if result.returncode == 0:
            raise AssertionError("非法角色包操作未被拒绝。")
        return {}
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise TypeError("命令输出必须是 JSON 对象。")
    return value


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="e8-visual-ip-pack-") as temporary:
        workspace = Path(temporary)
        identity = workspace / "identity.png"
        toy_style = workspace / "soft-toy-style.md"
        character_definition = workspace / "character.md"
        write_image(identity)
        write_text(character_definition, "# 角色：小曜\n\n## 身份锚点\n\n长发、双环耳饰、圆形棕色眼睛。\n")
        write_text(toy_style, "# 风格：软萌潮玩Q版\n\n大头短身、暖色粗线与圆润角色体块。\n")

        if (workspace / ".creator-space").exists():
            raise AssertionError("测试前不应存在 creator-space。")

        saved = run_json(
            "save-character",
            "--workspace-root", str(workspace),
            "--key", "xiaoyao",
            "--display-name", "小曜",
            "--identity-image", str(identity),
            "--character-definition", str(character_definition),
            "--style-id", "soft-toy-chibi",
            "--style-name", "软萌潮玩Q版",
            "--style-definition", str(toy_style),
        )
        if not Path(saved["character_dir"]).is_dir():
            raise AssertionError("首次保存未自动创建共享角色包。")
        if not (workspace / ".creator-space" / "visual-ip").is_dir():
            raise AssertionError("首次保存未创建最小 creator-space。")

        run_json(
            "save-character",
            "--workspace-root", str(workspace),
            "--key", "xiaoyao",
            "--display-name", "小曜",
            "--identity-image", str(identity),
            "--character-definition", str(character_definition),
            "--style-id", "soft-toy-chibi",
            "--style-name", "软萌潮玩Q版",
            "--style-definition", str(toy_style),
            expect_success=False,
        )

        custom_image = workspace / "marker.png"
        custom_style = workspace / "marker-style.md"
        write_image(custom_image, b"marker")
        write_text(custom_style, "# 自定义风格：马克笔角色\n\n粗细变化的墨线与克制马克笔叠色。\n")
        added = run_json(
            "add-style",
            "--workspace-root", str(workspace),
            "--key", "xiaoyao",
            "--style-id", "marker-character",
            "--style-name", "马克笔角色",
            "--style-image", str(custom_image),
            "--style-definition", str(custom_style),
        )
        if added["style_id"] != "marker-character":
            raise AssertionError("新增自定义风格结果错误。")

        resolved = run_json(
            "resolve",
            "--workspace-root", str(workspace),
            "--key", "xiaoyao",
            "--style-id", "marker-character",
        )
        if resolved["style"]["style_id"] != "marker-character":
            raise AssertionError("角色与自定义风格解析错误。")
        if not Path(resolved["identity_reference"]).is_file():
            raise AssertionError("身份锚点解析路径不存在。")
        if not Path(resolved["style"]["reference"]).is_file():
            raise AssertionError("风格锚点解析路径不存在。")

        custom_image_v2 = workspace / "marker-v2.png"
        custom_style_v2 = workspace / "marker-style-v2.md"
        write_image(custom_image_v2, b"marker-v2")
        write_text(custom_style_v2, "# 自定义风格：马克笔角色\n\n减少墨线噪点，保留马克笔叠色。\n")
        updated_style = run_json(
            "update-style",
            "--workspace-root", str(workspace),
            "--key", "xiaoyao",
            "--style-id", "marker-character",
            "--style-name", "马克笔角色",
            "--style-image", str(custom_image_v2),
            "--style-definition", str(custom_style_v2),
        )
        if not Path(updated_style["backup_dir"]).is_dir():
            raise AssertionError("更新自定义风格前没有创建备份。")

        identity_v2 = workspace / "identity-v2.png"
        character_v2 = workspace / "character-v2.md"
        write_image(identity_v2, b"identity-v2")
        write_text(character_v2, "# 角色：小曜\n\n## 身份锚点\n\n长发、双环耳饰、圆形棕色眼睛、成熟气质。\n")
        updated_character = run_json(
            "update-character",
            "--workspace-root", str(workspace),
            "--key", "xiaoyao",
            "--display-name", "小曜",
            "--identity-image", str(identity_v2),
            "--character-definition", str(character_v2),
            "--style-id", "soft-toy-chibi",
            "--style-name", "软萌潮玩Q版",
            "--style-definition", str(toy_style),
        )
        if not Path(updated_character["backup_dir"]).is_dir():
            raise AssertionError("更新人物前没有创建备份。")

        listing = run_json("list", "--workspace-root", str(workspace))
        if listing["count"] != 1:
            raise AssertionError(f"人物列表数量错误：{listing}")
        style_ids = [item["style_id"] for item in listing["characters"][0]["styles"]]
        if style_ids != ["soft-toy-chibi"]:
            raise AssertionError("人物核心更新后不应静默沿用旧人物的自定义风格锚点。")

        validation = run_json("validate", "--workspace-root", str(workspace))
        if validation["valid"] is not True or validation["character_count"] != 1 or validation["style_count"] != 1:
            raise AssertionError(f"最终角色包校验错误：{validation}")

        run_json(
            "save-character",
            "--workspace-root", str(workspace),
            "--key", "Invalid_Key",
            "--display-name", "错误",
            "--identity-image", str(identity),
            "--character-definition", str(character_definition),
            "--style-id", "soft-toy-chibi",
            "--style-name", "软萌潮玩Q版",
            "--style-definition", str(toy_style),
            expect_success=False,
        )
        print("smoke_lifecycle: PASS")


if __name__ == "__main__":
    main()
