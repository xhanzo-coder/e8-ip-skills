# 街头像素运行契约

首次正面人物运行必须创建 `run-contract.json`，并分别在生图前后调用：

```powershell
python -X utf8 scripts/validate_pixel_run.py --run-dir <运行目录> --phase pre
python -X utf8 scripts/validate_pixel_run.py --run-dir <运行目录> --phase post
```

## 生成前模板

```json
{
  "schema_version": "1.0",
  "style_id": "streetwear-pixel-sheet",
  "task_type": "base-character",
  "reference_maturity": "limited-multi-reference",
  "route": "accessory-purple",
  "status": "planned",
  "identity_references": ["用户身份图绝对路径"],
  "primary_style_reference": "所选路由正面裁图绝对路径",
  "secondary_style_references": ["所选路由头部裁图绝对路径"],
  "reference_order": [
    "所选路由正面裁图绝对路径",
    "用户身份图绝对路径",
    "所选路由头部裁图绝对路径"
  ],
  "full_sheet_reference": "所选路由完整三视图绝对路径",
  "full_sheet_passed_to_generation": false,
  "prompt_file": "prompts/candidate-v1.md",
  "candidate_file": null,
  "qa_file": null,
  "out_of_scope": [],
  "pixel_policy": {
    "nearest_neighbor_only": true,
    "anti_aliasing_forbidden": true,
    "gradient_forbidden": true,
    "palette_color_min": 16,
    "palette_color_max": 28,
    "accent_system_count": 1
  },
  "positive_anchors": {
    "pixel_anchor_1_uniform_grid": "PENDING",
    "pixel_anchor_2_limited_palette": "PENDING",
    "pixel_anchor_3_youth_proportion": "PENDING",
    "pixel_anchor_4_hair_clusters": "PENDING",
    "pixel_anchor_5_simple_face": "PENDING",
    "pixel_anchor_6_streetwear_volume": "PENDING",
    "pixel_anchor_7_relaxed_lower_body": "PENDING",
    "pixel_anchor_8_dark_accent": "PENDING"
  }
}
```

`route` 只能是 `accessory-purple` 或 `hair-accent-dark`。主参考、头部辅助参考和完整三视图必须属于同一路由。

## 生成后

- 填写 `candidate_file` 和 `qa_file`。
- 八项像素锚点逐项改为 `PASS` 或 `FAIL`。
- 全部通过时 `status` 为 `approved_candidate`。
- 任一失败时 `status` 为 `rejected`，不得向用户展示成可确认版本。
- `qa.md` 必须逐项记录八个锚点、像素网格、色板范围、强调色数量和可见证据。

运行契约证明参考顺序、色板政策和 QA 流程完整，但不替代视觉判断。
