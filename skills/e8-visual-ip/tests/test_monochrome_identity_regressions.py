from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_monochrome_run.py"
FIXTURES = (
    SKILL_ROOT
    / "evals"
    / "output"
    / "fixtures"
    / "monochrome-identity-regressions.json"
)
STYLE_ROOT = SKILL_ROOT / "assets" / "style-references" / "monochrome-manga-sheet"
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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_post(run_dir: Path, expect_success: bool) -> None:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--run-dir", str(run_dir), "--phase", "post"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    if not expect_success and result.returncode == 0:
        raise AssertionError("身份失败的候选被错误批准。")


def make_contract(run_dir: Path, identity: Path, case: dict[str, Any], status: str) -> dict[str, Any]:
    primary = str((STYLE_ROOT / "front-character.png").resolve())
    identity_path = str(identity.resolve())
    return {
        "schema_version": "2.0",
        "style_id": "monochrome-manga-sheet",
        "task_type": "base-character",
        "reference_maturity": "single-reference",
        "likeness": "recognizable",
        "reference_strategy": "identity-first",
        "single_candidate_only": True,
        "status": status,
        "identity_status": "FAIL",
        "identity_references": [identity_path],
        "primary_style_reference": primary,
        "secondary_style_references": [],
        "reference_order": [identity_path, primary],
        "full_sheet_reference": str((STYLE_ROOT / "reference.png").resolve()),
        "full_sheet_passed_to_generation": False,
        "negative_examples_passed_to_generation": False,
        "prompt_file": "prompts/candidate.md",
        "candidate_file": "candidate.png",
        "qa_file": "qa.md",
        "out_of_scope": [],
        "identity_anchors": case["identity_anchors"],
        "positive_anchors": {anchor: "PASS" for anchor in STYLE_ANCHOR_IDS},
    }


def main() -> None:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if fixtures["fixture_label"] != "file-backed fixture":
        raise AssertionError("回归集必须保留 file-backed fixture 标签。")

    for case in fixtures["cases"]:
        with tempfile.TemporaryDirectory(prefix=f"e8-{case['id']}-") as temporary:
            run_dir = Path(temporary)
            identity = run_dir / "identity.png"
            identity.write_bytes(b"identity")
            (run_dir / "candidate.png").write_bytes(b"candidate")
            write_text(run_dir / "analysis.md", f"# {case['person_label']} 身份分析\n")
            write_text(run_dir / "plan.md", "# 单张候选计划\n")
            write_text(run_dir / "prompts/candidate.md", "one candidate only\n")
            qa_lines = [
                "# QA",
                "- 身份层：FAIL",
                *[
                    f"- {anchor}: {result}"
                    for anchor, result in case["identity_anchors"].items()
                ],
                *[f"- {anchor}: PASS" for anchor in STYLE_ANCHOR_IDS],
            ]
            write_text(run_dir / "qa.md", "\n".join(qa_lines) + "\n")

            false_approval = make_contract(run_dir, identity, case, "approved_candidate")
            write_text(
                run_dir / "run-contract.json",
                json.dumps(false_approval, ensure_ascii=False, indent=2) + "\n",
            )
            run_post(run_dir, expect_success=False)

            rejected = make_contract(run_dir, identity, case, case["expected_status"])
            write_text(
                run_dir / "run-contract.json",
                json.dumps(rejected, ensure_ascii=False, indent=2) + "\n",
            )
            run_post(run_dir, expect_success=True)

    print("test_monochrome_identity_regressions: PASS")


if __name__ == "__main__":
    main()
