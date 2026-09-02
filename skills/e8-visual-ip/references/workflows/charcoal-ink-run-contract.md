# 黑灰墨线候选运行契约

本契约只用于 `charcoal-ink-chibi` 候选风格的首次正面 `base-character` 校准。

## 生成前

- `lifecycle_status` 必须为 `candidate`。
- 一次授权只能生成一张候选。
- 主风格参考必须是登记的 `reference.png`。
- `reference_order` 必须为主风格参考在前、1～2 张身份参考在后。
- Prompt 必须完整写入无彩色阶、比例、黑色墨线、实心黑发、面部语法、无阴影、参考隔离和纯背景八项契约。
- 身份与风格锚点均为 `PENDING`，候选图和 QA 为空。

## 生成后

- 身份与八项风格锚点逐项记录 `PASS` 或 `FAIL`。
- `approved_candidate` 只允许在全部身份锚点和风格锚点通过时使用。
- 任一项失败必须为 `rejected`，不得自动生成第二张。
- `qa.md` 必须记录每个锚点 ID 与身份层、风格层、任务层结果。

运行：

```text
python scripts/validate_charcoal_ink_run.py --run-dir <目录> --phase pre
python scripts/validate_charcoal_ink_run.py --run-dir <目录> --phase post
```
