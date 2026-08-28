#!/usr/bin/env python3
"""回归测试风格注册表、统一 Schema 关键字段与资产来源清单。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_style_registry.py"


def main() -> None:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--skill-dir", str(SKILL_ROOT)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    payload = json.loads(result.stdout)
    if payload["valid"] is not True:
        raise AssertionError("风格注册表未通过校验。")
    if payload["style_count"] != 3:
        raise AssertionError(f"当前内置风格数量错误：{payload['style_count']}")
    if payload["asset_count"] != 15:
        raise AssertionError(f"当前已登记风格资产数量错误：{payload['asset_count']}")
    style_ids = [entry["id"] for entry in payload["styles"]]
    if style_ids != ["soft-toy-chibi", "monochrome-manga-sheet", "streetwear-pixel-sheet"]:
        raise AssertionError(f"风格注册顺序或标识错误：{style_ids}")
    expected_catalog_pairs = {
        "soft-toy-chibi": (
            "assets/style-references/soft-toy-chibi/minimal-face-sheet.png",
            "assets/style-references/soft-toy-chibi/minimal-face-sheet.png",
        ),
        "monochrome-manga-sheet": (
            "assets/style-references/monochrome-manga-sheet/reference.png",
            "assets/style-references/monochrome-manga-sheet/front-character.png",
        ),
        "streetwear-pixel-sheet": (
            "assets/style-references/streetwear-pixel-sheet/accessory-purple-sheet.png",
            "assets/style-references/streetwear-pixel-sheet/accessory-purple-front.png",
        ),
    }
    observed_catalog_pairs = {
        entry["id"]: (entry["catalog_preview"], entry["catalog_primary_style"])
        for entry in payload["styles"]
    }
    if observed_catalog_pairs != expected_catalog_pairs:
        raise AssertionError(f"风格目录预览或默认主参考错误：{observed_catalog_pairs}")
    print("test_style_registry: PASS")


if __name__ == "__main__":
    main()
