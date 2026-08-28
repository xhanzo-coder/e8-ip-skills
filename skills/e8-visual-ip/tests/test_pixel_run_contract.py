from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts/validate_pixel_run.py"
STYLE_ROOT = SKILL_ROOT / "assets/style-references/streetwear-pixel-sheet"
ANCHOR_IDS = (
    "pixel_anchor_1_uniform_grid",
    "pixel_anchor_2_limited_palette",
    "pixel_anchor_3_youth_proportion",
    "pixel_anchor_4_hair_clusters",
    "pixel_anchor_5_simple_face",
    "pixel_anchor_6_streetwear_volume",
    "pixel_anchor_7_relaxed_lower_body",
    "pixel_anchor_8_dark_accent",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_validator(run_dir: Path, phase: str, expect_success: bool) -> None:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--run-dir",
            str(run_dir),
            "--phase",
            phase,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    if not expect_success and result.returncode == 0:
        raise AssertionError("非法像素运行契约未被拒绝。")


def make_contract(run_dir: Path, identity: Path) -> dict[str, object]:
    primary = str((STYLE_ROOT / "accessory-purple-front.png").resolve())
    secondary = str((STYLE_ROOT / "accessory-purple-head.png").resolve())
    return {
        "schema_version": "1.0",
        "style_id": "streetwear-pixel-sheet",
        "task_type": "base-character",
        "reference_maturity": "limited-multi-reference",
        "route": "accessory-purple",
        "status": "planned",
        "identity_references": [str(identity.resolve())],
        "primary_style_reference": primary,
        "secondary_style_references": [secondary],
        "reference_order": [primary, str(identity.resolve()), secondary],
        "full_sheet_reference": str(
            (STYLE_ROOT / "accessory-purple-sheet.png").resolve()
        ),
        "full_sheet_passed_to_generation": False,
        "prompt_file": "prompts/candidate-v1.md",
        "candidate_file": None,
        "qa_file": None,
        "out_of_scope": [],
        "pixel_policy": {
            "nearest_neighbor_only": True,
            "anti_aliasing_forbidden": True,
            "gradient_forbidden": True,
            "palette_color_min": 16,
            "palette_color_max": 28,
            "accent_system_count": 1,
        },
        "positive_anchors": {anchor: "PENDING" for anchor in ANCHOR_IDS},
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="e8-pixel-run-") as temporary:
        run_dir = Path(temporary)
        identity = run_dir / "identity.png"
        identity.write_bytes(b"identity")
        write_text(run_dir / "analysis.md", "# 身份分析\n")
        write_text(run_dir / "plan.md", "# 运行计划\n")
        write_text(run_dir / "prompts/candidate-v1.md", "# 完整Prompt\n")

        contract = make_contract(run_dir, identity)
        write_text(
            run_dir / "run-contract.json",
            json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        )
        run_validator(run_dir, "pre", expect_success=True)

        candidate = run_dir / "candidate-v1.png"
        candidate.write_bytes(b"candidate")
        qa_lines = ["# QA", *[f"- {anchor}: PASS" for anchor in ANCHOR_IDS]]
        write_text(run_dir / "qa.md", "\n".join(qa_lines) + "\n")
        contract["status"] = "approved_candidate"
        contract["candidate_file"] = candidate.name
        contract["qa_file"] = "qa.md"
        contract["positive_anchors"] = {anchor: "PASS" for anchor in ANCHOR_IDS}
        write_text(
            run_dir / "run-contract.json",
            json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        )
        run_validator(run_dir, "post", expect_success=True)

        invalid = make_contract(run_dir, identity)
        invalid["pixel_policy"]["nearest_neighbor_only"] = False
        write_text(
            run_dir / "run-contract.json",
            json.dumps(invalid, ensure_ascii=False, indent=2) + "\n",
        )
        run_validator(run_dir, "pre", expect_success=False)

        print("test_pixel_run_contract: PASS")


if __name__ == "__main__":
    main()
