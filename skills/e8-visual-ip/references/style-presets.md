# 风格 Preset

Preset 是风格已经由用户选择或明确委托 Skill 代选之后，组合人物方向、相似程度和配色策略的内部快捷方式。Preset 不能跳过首次风格目录，也不能把未指定风格解释成默认软萌潮玩。显式指定的单独维度始终覆盖 Preset。

| Preset | 人物方向 | 相似程度 | 风格 | 配色策略 | 适合 |
|---|---|---|---|---|---|
| `recognizable-toy` | `recognizable-chibi` | `recognizable` | `soft-toy-chibi` | 自动整理身份色并角色化穿搭 | 已选择软萌潮玩后的个人分身、生活方式IP、正侧背设定 |
| `graphic-toy` | `graphic-chibi` | `interpreted` | `soft-toy-chibi` | 柔和主色＋高识别招牌系统 | 更抽象的潮玩角色、手账人物、贴纸和周边 |
| `symbolic-toy` | `symbolic-mascot` | `symbolic` | `soft-toy-chibi` | 单主色＋固定强调色载体 | 保留人物结构的符号化潮玩吉祥物 |
| `interpreted-mono` | `recognizable-chibi` | `interpreted` | `monochrome-manga-sheet` | 身份色转译为黑白形状与固定载体 | 已选择黑白漫画后的个人分身、角色设定稿和三视图 |
| `graphic-mono` | `graphic-chibi` | `interpreted` | `monochrome-manga-sheet` | 强化实心黑块与白色负空间 | 更符号化的黑白漫画角色、头像和贴纸 |
| `interpreted-pixel` | `recognizable-chibi` | `interpreted` | `streetwear-pixel-sheet` | 从人物身份色中整理有限色板 | 可辨认的像素个人分身、头像和三视图 |
| `graphic-pixel` | `graphic-chibi` | `interpreted` | `streetwear-pixel-sheet` | 强化像素剪影并压缩为有限色板 | 更符号化的像素角色、头像和游戏式立绘 |

## 覆盖例子

- 用户只说“帮我设计个人Q版IP” → 先展示风格目录；选择软萌潮玩后才使用 `recognizable-toy`。
- 用户要求更抽象、缩小后识别 → `graphic-toy`。
- 用户要求吉祥物化、不要真人脸 → `symbolic-toy`，同时说明它仍保留软萌潮玩形状语法。
- 用户上传朴素正装照但未指定风格 → 先展示风格目录；选择软萌潮玩后可使用 `recognizable-toy`。正装只提供待判断气质，不自动复制服装。
- 用户明确要最终纯黑白漫画人物或黑白三视图 → `interpreted-mono`；用户要求更像本人时只把相似度提升到 `recognizable`。
- 用户要更抽象的黑白角色、强调剪影与负空间 → `graphic-mono`。
- 用户明确要像素人物 → 根据所需辨识度选择 `interpreted-pixel` 或 `graphic-pixel`；配色、服装和人物特征均来自用户，不从参考图固定继承。
- 用户提供一套与三个内置风格明显不同的新参考图 → 不套用本表，进入自定义风格候选流程。

Preset 是推荐入口，不是确认结果。正式人物和新增自定义风格仍需用户明确确认。
