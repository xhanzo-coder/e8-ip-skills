# 像素角色运行契约

本契约校验 `streetwear-pixel-sheet` 风格的一张正面 `base-character` 候选。风格 ID 为兼容已有角色包而保留；它表示通用像素画法，不限定暗黑、街头、发型、眼镜、耳饰、服装、性别或配色。

## 生成前

- `route` 固定为 `generic-pixel`，不得根据用户的外貌或穿搭拆分路线。
- 主参考固定为 `reference-01.png`；`reference-02.png` 仅可作为补充像素结构的辅助参考。
- 两张参考均只提供统一像素网格、有限色板、轮廓概括和体块画法，不提供人物身份。
- `reference_order` 必须为主风格参考、全部身份图、可选辅助风格参考。
- 发型、眼镜、耳饰、服装和配色必须来自用户照片、文字信息与已确认方案；不得复制参考人物。
- 统一像素网格、禁用抗锯齿与渐变，并使用有限离散色板。
- 八项风格锚点生成前均为 `PENDING`。

## 生成后

- 八项锚点逐项写入 QA。
- 全部通过才能标记 `approved_candidate`；任一失败必须为 `rejected`。
- 正面人物确认后，才可继续制作已支持的头像或三视图。

```text
python scripts/validate_pixel_run.py --run-dir <目录> --phase pre
python scripts/validate_pixel_run.py --run-dir <目录> --phase post
```
