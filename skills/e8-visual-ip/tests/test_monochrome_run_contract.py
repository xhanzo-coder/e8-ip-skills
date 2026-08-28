from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_monochrome_run.py"
STYLE_ROOT = SKILL_ROOT / "assets/style-references/monochrome-manga-sheet"
IDENTITY_ANCHOR_IDS = (
    "identity_anchor_1_face_proportion",
    "identity_anchor_2_hairline_forehead",
    "identity_anchor_3_eye_brow_relation",
    "identity_anchor_4_mid_lower_face",
    "identity_anchor_5_age_mood",
)
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


def write_contract(run_dir: Path, contract: dict[str, object]) -> None:
    write_text(
        run_dir / "run-contract.json",
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
    )


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
        raise AssertionError("非法黑白运行契约未被拒绝。")


def make_identity_first_contract(identity: Path) -> dict[str, object]:
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
        "status": "planned",
        "identity_status": "PENDING",
        "identity_references": [identity_path],
        "primary_style_reference": primary,
        "secondary_style_references": [],
        "reference_order": [identity_path, primary],
        "full_sheet_reference": str((STYLE_ROOT / "reference.png").resolve()),
        "full_sheet_passed_to_generation": False,
        "negative_examples_passed_to_generation": False,
        "prompt_file": "prompts/candidate-v1.md",
        "candidate_file": None,
        "qa_file": None,
        "out_of_scope": [],
        "identity_anchors": {anchor: "PENDING" for anchor in IDENTITY_ANCHOR_IDS},
        "positive_anchors": {anchor: "PENDING" for anchor in STYLE_ANCHOR_IDS},
    }


def finalize_contract(
    run_dir: Path,
    contract: dict[str, object],
    *,
    identity_failure: str | None = None,
    status: str,
) -> None:
    candidate = run_dir / "candidate-v1.png"
    candidate.write_bytes(b"candidate")
    identity_results = {
        anchor: "FAIL" if anchor == identity_failure else "PASS"
        for anchor in IDENTITY_ANCHOR_IDS
    }
    style_results = {anchor: "PASS" for anchor in STYLE_ANCHOR_IDS}
    identity_status = "FAIL" if identity_failure is not None else "PASS"
    qa_lines = [
        "# QA",
        f"- 身份层：{identity_status}",
        *[f"- {anchor}: {result}" for anchor, result in identity_results.items()],
        *[f"- {anchor}: {result}" for anchor, result in style_results.items()],
    ]
    write_text(run_dir / "qa.md", "\n".join(qa_lines) + "\n")
    contract["status"] = status
    contract["identity_status"] = identity_status
    contract["candidate_file"] = candidate.name
    contract["qa_file"] = "qa.md"
    contract["identity_anchors"] = identity_results
    contract["positive_anchors"] = style_results
    write_contract(run_dir, contract)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="e8-monochrome-run-") as temporary:
        run_dir = Path(temporary)
        identity = run_dir / "identity.png"
        identity.write_bytes(b"identity")
        write_text(run_dir / "analysis.md", "# 身份分析\n\n已记录五项身份指纹。\n")
        write_text(run_dir / "plan.md", "# 运行计划\n\n每轮只生成一张候选。\n")
        write_text(run_dir / "prompts/candidate-v1.md", "# 完整 Prompt\n\none candidate only\n")

        valid = make_identity_first_contract(identity)
        write_contract(run_dir, valid)
        run_validator(run_dir, "pre", expect_success=True)

        approved = make_identity_first_contract(identity)
        finalize_contract(run_dir, approved, status="approved_candidate")
        run_validator(run_dir, "post", expect_success=True)

        rejected = make_identity_first_contract(identity)
        finalize_contract(
            run_dir,
            rejected,
            identity_failure="identity_anchor_3_eye_brow_relation",
            status="rejected",
        )
        run_validator(run_dir, "post", expect_success=True)

        false_approval = make_identity_first_contract(identity)
        finalize_contract(
            run_dir,
            false_approval,
            identity_failure="identity_anchor_4_mid_lower_face",
            status="approved_candidate",
        )
        run_validator(run_dir, "post", expect_success=False)

        wrong_strategy = make_identity_first_contract(identity)
        wrong_strategy["reference_strategy"] = "style-first"
        write_contract(run_dir, wrong_strategy)
        run_validator(run_dir, "pre", expect_success=False)

        hidden_second_image = make_identity_first_contract(identity)
        hidden_second_image["single_candidate_only"] = False
        write_contract(run_dir, hidden_second_image)
        run_validator(run_dir, "pre", expect_success=False)

        style_face_contamination = make_identity_first_contract(identity)
        face_detail = str((STYLE_ROOT / "face-hair-detail.png").resolve())
        style_face_contamination["secondary_style_references"] = [face_detail]
        style_face_contamination["reference_order"] = [
            str(identity.resolve()),
            str((STYLE_ROOT / "front-character.png").resolve()),
            face_detail,
        ]
        write_contract(run_dir, style_face_contamination)
        run_validator(run_dir, "pre", expect_success=False)

        print("test_monochrome_run_contract: PASS")


if __name__ == "__main__":
    main()
