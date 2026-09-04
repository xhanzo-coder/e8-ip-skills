# 暗黑街头像素候选运行契约

本契约只校验新参考体系下的一张正面 `base-character` 候选。

## 生成前

- `route` 只能是 `glasses-cyan` 或 `long-hair-gold`。
- 主参考必须分别为 `glasses-cyan.png` 或 `long-hair-gold.png`。
- 新参考均为完整正面图，必须真实传入生成工具；不再使用旧版三视图和头部裁图。
- `reference_order` 为主风格参考在前、身份图在后，辅助参考必须为空。
- 统一像素网格、禁用抗锯齿与渐变、限制色板并只允许一个强调系统。
- 八项风格锚点生成前均为 `PENDING`。

## 生成后

- 八项锚点逐项写入 QA。
- 全部通过才能标记 `approved_candidate`；任一失败必须为 `rejected`。
- 候选仍不代表三视图、头像或动作已经获得验证。

```text
python scripts/validate_pixel_run.py --run-dir <目录> --phase pre
python scripts/validate_pixel_run.py --run-dir <目录> --phase post
```
