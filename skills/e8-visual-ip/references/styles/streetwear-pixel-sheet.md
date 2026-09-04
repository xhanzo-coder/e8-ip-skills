---
id: streetwear-pixel-sheet
display_name: 暗黑街头像素角色风
lifecycle_status: candidate
aliases: [街头像素人物, 像素个人IP, 暗黑像素角色, 青年像素人物, 像素角色设定]
transformation_policy: structural-redraw
reference_maturity: limited-multi-reference
default_likeness: interpreted
supported_outputs: []
unverified_outputs: [base-character, turnaround, avatar, expression, action, sticker, outfit, scene]
reference_assets:
  glasses_cyan: ../../assets/style-references/streetwear-pixel-sheet/glasses-cyan.png
  long_hair_gold: ../../assets/style-references/streetwear-pixel-sheet/long-hair-gold.png
---

# 暗黑街头像素角色风

## 当前状态

两张新参考已替换旧 Pinterest 资产。由于新参考只有正面人物，当前风格降为 `candidate`：不进入正式目录、不自动推荐、不声明任何稳定产物。完成真实校准前不得沿用旧参考的三视图结论。

## 共同视觉语法

- 约 3.1～3.6 头身，头大、肩窄、身体较直，完整全身正面站姿。
- 统一方形像素网格，轮廓和内部细节均由清晰阶梯像素组成。
- 黑色与深灰占主导，肤色为少量暖色块；每个人物最多一个高饱和强调色。
- 头发使用大型黑色像素簇，只保留少量深灰高光簇。
- 眼睛、眉毛、鼻子和嘴使用少量大像素块，不允许高清动漫五官缩小后再马赛克化。
- 街头服装以宽松外套、内搭、阔腿裤和厚底鞋形成大型暗色体块。
- 纯白或近白背景，无场景、文字、地面投影和柔焦光晕。

## 两个参考方向

### `glasses-cyan`

- 短发、眼镜或清楚面部配饰承担识别。
- 黑灰外套、米白内搭与阔腿裤。
- 青色只用于袖口和鞋面小块强调。
- 当前作为目录预览和默认主参考。

### `long-hair-gold`

- 长发外轮廓、耳饰或成熟气质承担识别。
- 黑色长发、黑灰夹克和宽松长裤。
- 金色只用于耳饰、扣件等少量强调。
- 只有用户看过差异并明确选择后才能使用，不能依据性别静默切换。

## 八项硬门

1. `pixel_anchor_1_uniform_grid`：全图像素块尺度一致，无平滑曲线和抗锯齿插画边缘。
2. `pixel_anchor_2_dark_palette`：黑灰主导，肤色有限，仅一个青色或金色强调系统。
3. `pixel_anchor_3_compact_youth_proportion`：约 3.1～3.6 头身，不得恢复真人或时装模特比例。
4. `pixel_anchor_4_hair_clusters`：头发由大型黑色像素簇构成，不逐缕绘制。
5. `pixel_anchor_5_simple_face`：五官使用少量大像素，禁止玻璃虹膜和精细妆容。
6. `pixel_anchor_6_streetwear_volume`：外套、阔腿裤和鞋形成清楚暗色体块。
7. `pixel_anchor_7_single_accent`：青色或金色只能选择一个，不混合两个参考的强调色。
8. `pixel_anchor_8_clean_fullbody`：单人完整全身、正面、白底、无场景文字和投影。

## 身份与参考隔离

默认相似度为 `interpreted`。人物身份优先保留发型剪影、发际线、眼镜／耳饰、眉眼气质、脸型方向和年龄神态。禁止复制参考人物的具体脸、眼镜、耳饰、发型、服装和配色组合；只有用户明确选择相应参考方向后，才迁移其抽象配色系统。

## Prompt 风格段

```text
使用 structural-redraw 在统一方形像素网格上重构一个暗黑街头像素角色。人物约 3.1～3.6 头身，大头窄肩、短躯干、宽松外套、阔腿裤和厚底鞋形成清楚体块。黑色与深灰占主导，肤色只用少量离散色阶，并且只能选择一个强调系统：glasses-cyan 使用少量青色，long-hair-gold 使用少量金色；禁止混用。头发由大型黑色像素簇和极少深灰高光簇构成，五官只用少量大像素表达。所有曲线必须变成阶梯像素边缘，不得使用抗锯齿、柔光、渐变、半厚涂或高清插画套马赛克。输出单人完整全身正面角色，纯白或近白背景，无文字、场景和地面投影。不得复制参考人物的具体脸、眼镜、耳饰、发型或整套服装。
```

## 当前覆盖边界

两张参考只证明短发眼镜与长发耳饰两种正面角色共享同一暗黑像素语法。侧面、背面、三视图、头像、动作、表情、换装和场景全部未验证。首次只能生成一张正面候选，任一硬门失败即 `rejected`。

## 升级条件

至少完成两种不同身份结构的正面校准并由用户确认，再完成一组由已确认正面母图扩展的侧面与背面测试，才能恢复为正式目录风格。已通过产物才能进入 `supported_outputs`。
