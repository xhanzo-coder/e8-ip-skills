#!/usr/bin/env python3
"""Regression test for the charcoal-ink-chibi candidate run contract."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_charcoal_ink_run.py"
STYLE_REFERENCE = (
    SKILL_ROOT / "assets" / "style-references" / "charcoal-ink-chibi" / "reference.png"
)
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z4QAAAABJRU5ErkJggg=="
)
IDENTITY_IDS = (
    "identity_face_proportion",
    "identity_hairline_silhouette",
    "identity_eye_brow_relation",
    "identity_lower_face_relation",
    "identity_age_mood",
)
STYLE_IDS = (
    "charcoal_anchor_1_compact_ratio",
    "charcoal_anchor_2_head_limb_contrast",
    "charcoal_anchor_3_black_line_hierarchy",
    "charcoal_anchor_4_achromatic_palette",
    "charcoal_anchor_5_solid_black_hair",
    "charcoal_anchor_6_minimal_face",
    "charcoal_anchor_7_large_garment_blocks",
    "charcoal_anchor_8_clean_presentation",
)
PROMPT_KEYS = (
    "compact_ratio",
    "black_line_hierarchy",
    "achromatic_palette",
    "solid_black_hair",
    "minimal_face_grammar",
    "large_garment_blocks",
    "no_shading_or_texture",
    "reference_content_isolation",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: dict[str, object]) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run_validator(run_dir: Path, phase: str, expect_success: bool) -> None:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--run-dir", str(run_dir), "--phase", phase],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    if not expect_success and result.returncode == 0:
        raise AssertionError(f"Expected {phase} validation to fail.")


def make_contract(identity: Path, prompt: Path) -> dict[str, object]:
    primary = str(STYLE_REFERENCE)
    identity_path = str(identity)
    return {
        "schema_version": "1.0",
        "style_id": "charcoal-ink-chibi",
        "lifecycle_status": "candidate",
        "task": "base-character",
        "reference_maturity": "single-reference",
        "transformation_policy": "structural-redraw",
        "likeness": "interpreted",
        "single_candidate_only": True,
        "identity_references": [identity_path],
        "primary_style_reference": primary,
        "reference_order": [primary, identity_path],
        "full_sheet_passed_to_generation": True,
        "negative_examples_passed_to_generation": False,
        "prompt_file": str(prompt),
        "prompt_contract": {key: True for key in PROMPT_KEYS},
        "out_of_scope": ["turnaround", "expression", "scene"],
        "identity_anchors": {key: "PENDING" for key in IDENTITY_IDS},
        "style_anchors": {key: "PENDING" for key in STYLE_IDS},
        "identity_status": "PENDING",
        "style_status": "PENDING",
        "task_status": "PENDING",
        "status": "planned",
        "candidate_file": None,
        "qa_file": None,
    }


def main() -> None:
    if not STYLE_REFERENCE.is_file():
        raise FileNotFoundError(f"Missing style reference: {STYLE_REFERENCE}")

    with tempfile.TemporaryDirectory(prefix="e8-charcoal-ink-contract-") as temporary:
        run_dir = Path(temporary)
        identity = run_dir / "identity.png"
        candidate = run_dir / "candidate.png"
        prompt = run_dir / "prompts" / "front.md"
        qa = run_dir / "qa.md"
        identity.write_bytes(PNG_1X1)
        write_text(run_dir / "analysis.md", "# Analysis\n")
        write_text(run_dir / "plan.md", "# Plan\n")
        write_text(prompt, "# Charcoal ink prompt\n")

        contract = make_contract(identity, prompt)
        write_json(run_dir / "run-contract.json", contract)
        run_validator(run_dir, "pre", expect_success=True)

        invalid = make_contract(identity, prompt)
        invalid["reference_order"] = [str(identity), str(STYLE_REFERENCE)]
        write_json(run_dir / "run-contract.json", invalid)
        run_validator(run_dir, "pre", expect_success=False)

        candidate.write_bytes(PNG_1X1)
        qa_lines = [
            "# QA",
            "身份层：PASS",
            "风格层：PASS",
            "任务层：PASS",
            *IDENTITY_IDS,
            *STYLE_IDS,
        ]
        write_text(qa, "\n".join(qa_lines) + "\n")
        approved = make_contract(identity, prompt)
        approved["identity_anchors"] = {key: "PASS" for key in IDENTITY_IDS}
        approved["style_anchors"] = {key: "PASS" for key in STYLE_IDS}
        approved["identity_status"] = "PASS"
        approved["style_status"] = "PASS"
        approved["task_status"] = "PASS"
        approved["status"] = "approved_candidate"
        approved["candidate_file"] = str(candidate)
        approved["qa_file"] = str(qa)
        write_json(run_dir / "run-contract.json", approved)
        run_validator(run_dir, "post", expect_success=True)

        rejected = approved.copy()
        rejected["style_anchors"] = {
            key: "FAIL" if key == "charcoal_anchor_4_achromatic_palette" else "PASS"
            for key in STYLE_IDS
        }
        rejected["style_status"] = "FAIL"
        rejected["status"] = "rejected"
        write_text(
            qa,
            "\n".join(
                [
                    "# QA",
                    "身份层：PASS",
                    "风格层：FAIL",
                    "任务层：PASS",
                    *IDENTITY_IDS,
                    *STYLE_IDS,
                ]
            )
            + "\n",
        )
        write_json(run_dir / "run-contract.json", rejected)
        run_validator(run_dir, "post", expect_success=True)

    print("test_charcoal_ink_run_contract: PASS")


if __name__ == "__main__":
    main()
