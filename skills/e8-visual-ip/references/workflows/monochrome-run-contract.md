# 极简黑白漫画运行契约 2.0

首次正面人物运行必须创建 `run-contract.json`，并在生图前后分别执行：

```powershell
python -X utf8 scripts/validate_monochrome_run.py --run-dir <运行目录> --phase pre
python -X utf8 scripts/validate_monochrome_run.py --run-dir <运行目录> --phase post
```

## 生成前模板

下面是默认 `recognizable` 路线。每次授权只允许一张当前阶段候选。

```json
{
  "schema_version": "2.0",
  "style_id": "monochrome-manga-sheet",
  "task_type": "base-character",
  "reference_maturity": "single-reference",
  "likeness": "recognizable",
  "reference_strategy": "identity-first",
  "single_candidate_only": true,
  "status": "planned",
  "identity_status": "PENDING",
  "identity_references": ["主身份图绝对路径"],
  "primary_style_reference": "风格正面裁图绝对路径/front-character.png",
  "secondary_style_references": [],
  "reference_order": [
    "主身份图绝对路径",
    "风格正面裁图绝对路径/front-character.png"
  ],
  "full_sheet_reference": "完整三视图绝对路径/reference.png",
  "full_sheet_passed_to_generation": false,
  "negative_examples_passed_to_generation": false,
  "prompt_file": "prompts/candidate-v1.md",
  "candidate_file": null,
  "qa_file": null,
  "out_of_scope": [],
  "identity_anchors": {
    "identity_anchor_1_face_proportion": "PENDING",
    "identity_anchor_2_hairline_forehead": "PENDING",
    "identity_anchor_3_eye_brow_relation": "PENDING",
    "identity_anchor_4_mid_lower_face": "PENDING",
    "identity_anchor_5_age_mood": "PENDING"
  },
  "positive_anchors": {
    "anchor_1_identity_adaptive_eyes": "PENDING",
    "anchor_2_hair_silhouette": "PENDING",
    "anchor_3_stylized_structure": "PENDING",
    "anchor_4_oversized_garment": "PENDING",
    "anchor_5_relaxed_lower_body": "PENDING",
    "anchor_6_line_hierarchy": "PENDING",
    "anchor_7_black_mass": "PENDING",
    "anchor_8_identity_aligned_mood": "PENDING"
  }
}
```

## 参考策略

### `identity-first`

适用于 `recognizable` 与 `close`：

```text
主身份图 → front-character.png → 可选第二张身份图
```

- `identity_references` 最多两张，第一张必须是清晰主身份图。
- `secondary_style_references` 必须为空。
- `face-hair-detail.png` 不得传入图片工具。

### `style-first`

只适用于用户明确选择的 `interpreted`：

```text
front-character.png → 一张身份图 → 可选 face-hair-detail.png
```

该路线不承诺“别人能认出本人”。

## 生成后

- 填写 `candidate_file` 和 `qa_file`。
- 五项身份锚点和八项风格锚点全部改为 `PASS` 或 `FAIL`。
- 五项身份锚点全部通过时 `identity_status` 为 `PASS`；任一失败时必须为 `FAIL`。
- 只有 `identity_status=PASS` 且八项风格锚点全部通过时，`status` 才能是 `approved_candidate`。
- 身份或风格任一失败时，`status` 必须是 `rejected`。
- `qa.md` 必须逐项写出五个身份锚点、八个风格锚点及其可见证据。
- 失败后停止，不自动生成头像、脸部校准图或第二版；额外校准必须重新获得用户授权。

运行契约只证明文件、参考顺序、单张边界和 QA 状态一致，不能替代视觉判断或用户正式确认。
