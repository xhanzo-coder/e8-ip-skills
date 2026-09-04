---
id: streetwear-pixel-sheet
display_name: 像素角色设定风
lifecycle_status: active
aliases: [像素个人IP, 像素人物, 像素三视图, 像素角色, 像素角色设定]
transformation_policy: structural-redraw
reference_maturity: limited-multi-reference
default_likeness: interpreted
supported_outputs: [base-character, turnaround, avatar]
unverified_outputs: [expression, action, sticker, outfit, scene]
reference_assets:
  reference_01: ../../assets/style-references/streetwear-pixel-sheet/reference-01.png
  reference_02: ../../assets/style-references/streetwear-pixel-sheet/reference-02.png
---

# 像素角色设定风

## 目标

把真实人物重构为可复用的像素角色：统一像素网格、有限色板、简化五官、清楚人物剪影和完整全身结构。两张参考图只用于证明像素画法，不定义用户必须具有的发型、眼镜、耳饰、服装、性别或配色。

## 参考原则

- `reference-01.png` 与 `reference-02.png` 是同一通用像素风的两个示例，不是两类人物模板。
- 默认以 `reference-01.png` 为主风格参考；需要补充长发像素簇或另一种服装体块时，可以把 `reference-02.png` 作为辅助风格参考。
- 选择参考图只取决于本次需要补充的绘画结构，不得依据用户的长短发、眼镜、耳饰或性别固定路由。
- 禁止复制参考人物的脸、发型、眼镜、耳饰、黑色服装、青色／金色点缀和身体身份。

## 八项风格锚点

1. `pixel_anchor_1_uniform_grid`：所有轮廓与细节遵循统一方形像素网格，没有平滑矢量曲线。
2. `pixel_anchor_2_limited_palette`：使用有限离散色板，每个材质只有基础色、少量阴影和高光色阶。
3. `pixel_anchor_3_youth_proportion`：约 3.1～3.8 头身，大头窄肩、短躯干，不恢复真人比例。
4. `pixel_anchor_4_hair_clusters`：头发先形成身份剪影，再用大型像素簇表达层次，不逐缕绘制。
5. `pixel_anchor_5_simple_face`：眼眉鼻口只使用少量清楚像素，不生成精细动漫五官。
6. `pixel_anchor_6_clothing_blocks`：无论用户选择什么服装，都使用清楚、可跨视角复用的大型像素体块表达。
7. `pixel_anchor_7_identity_adaptation`：发型、眼镜、耳饰、服装和配色全部来自用户身份与方案，不从参考人物照搬。
8. `pixel_anchor_8_clean_fullbody`：单人完整全身、白色或近白背景，无文字、场景和地面投影。

## Prompt 风格段

```text
使用 structural-redraw 在统一方形像素网格上重构一个个人像素角色。人物约 3.1～3.8 头身，大头窄肩、短躯干，头发、服装、手脚和鞋由清楚的大型像素簇构成。使用有限离散色板，每个材质只保留基础色、1～2 层阴影和最多一层高光；禁止抗锯齿、柔光、渐变、半厚涂和高清插画套马赛克。五官只用少量大像素表达。发型、眼镜、耳饰、服装、身份色和强调色必须来自用户人物方案，不得复制参考图中的具体人物内容。输出单人完整全身角色，纯白或近白背景，无文字、场景和地面投影。
```

## 生成后硬门

- 像素尺度不统一，或存在平滑边缘、抗锯齿和柔焦。
- 结果是普通插画后加马赛克，而不是从像素网格重构。
- 人物超过约 3.8 头身，或恢复真人／模特比例。
- 五官、发丝和服装细节过密，不符合像素概括。
- 复制任一参考人物的长短发、眼镜、耳饰、服装或配色组合。
- 背景出现文字、场景、渐变或明显投影。

任一项出现即 `rejected`。正面人物确认后，才能继续侧面、背面和三视图；三视图能力来自角色结构工作流，不把参考人物特征固定到用户角色。
