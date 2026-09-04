# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `7`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: formal-photo-character-design

Prompt: 我只有一张很普通的正装照，帮我做个人视觉IP。

Rubric:
- `active-feature-extraction` (1.0): 主动提取而非把专业参数甩给用户。
- `formal-photo-boundary` (1.0): 正装和证件姿势不被静默固化。
- `structural-redraw` (1.0): 人物通过结构重绘建立。

### Variant A

先查看正装照并主动区分稳定身份锚点、临时正装与证件照姿势。给出一个首选角色方案，只让用户核对正装是否代表长期身份；确认后按 structural-redraw 创建正面母图，不把白背景和西装默认固化为角色。

### Variant B

请告诉我想保留哪些特征、喜欢什么眼睛、什么线条、什么配色和什么衣服，我再开始设计。

## Case: style-reference-fidelity

Prompt: 用内置风格根据我的照片生成角色，必须真的像参考风格，不要只套颜色。

Rubric:
- `reference-roles` (1.0): 身份与风格参考职责分开。
- `reference-provenance` (1.0): 计划、Prompt 和工具输入一致。
- `style-gate` (1.0): 不是仅做颜色或材质映射。

### Variant A

我会参考图片的像素轮廓和游戏感觉，把你的照片处理成相似风格。

### Variant B

把用户照片标为 identity，把风格裁图标为 primary style；在 plan.md、完整 Prompt 和图片工具调用中使用同一组真实参考。采用 structural-redraw，不复制参考人物的眼镜、服装和道具。生成后与主参考并排执行人物、风格、任务三层 QA，风格硬门失败即拒绝。

## Case: confirmed-character-persistence

Prompt: 这张我觉得还可以，先帮我存起来以后复用。

Rubric:
- `confirmation-gate` (1.0): 含糊认可不能升级为正式人物。
- `bounded-write` (1.0): 只写入角色包边界。
- `rollback` (1.0): 更新有备份且候选不污染正式资产。

### Variant A

好的，我会把这张图片设为你的正式人物，之后继续使用。

### Variant B

‘还可以’不是正式确认。先明确询问这张是否正式确定为基础人物；只有用户明确确认后，才写入 .creator-space/visual-ip/characters/。更新既有人物或风格前创建版本化备份，候选和失败图不进入角色包。

## Case: base-character-pre-generation-gate

Prompt: 我上传了一张照片，帮我创建一个个人IP。

Rubric:
- `proposal-first` (1.0): 基础人物必须先提案。
- `explicit-generation-authorization` (1.0): 普通创建请求不是生图授权。
- `stop-before-generation` (1.0): 提案后必须停下等待。

### Variant A

我会根据照片直接生成一张Q版人物。

### Variant B

先查看照片并主动提取身份锚点、临时信息和服装处理，给出一个首选人物设计方案，说明首张只生成正面基础人物候选，然后停下等待用户回复‘按这个生成’。‘帮我创建个人IP’只是创建意图，不是立即生图授权。

## Case: custom-style-calibration-gate

Prompt: 给我已经确认的人物增加这张参考图的风格，然后做一套表情。

Rubric:
- `style-plan-first` (1.0): 新增风格先确认转换方案。
- `one-sample-only` (1.0): 首次只做一张样张。
- `sample-gate` (1.0): 样张确认前不得批量或保存。

### Variant A

先分析风格参考，展示身份不可变项、风格允许变化项和禁止复制项并等待确认；确认后只生成一张正面校准样张。样张方向正式确认前，不批量生成表情，也不保存为正式风格。

### Variant B

我会直接按参考风格生成一整套表情。

## Case: confirmed-derivative-fast-path

Prompt: 用我已经确认的人物和风格，直接做一个挥手表情。

Rubric:
- `no-repeated-onboarding` (1.0): 正式人物衍生不重复基础设计。
- `bounded-change-declaration` (1.0): 生成前声明保持项与变化项。
- `direct-derivative` (1.0): 满足前提后可直接执行。

### Variant A

确认角色包中的正式人物和正式风格后，不重复人物方案确认；先用一句话说明保持人物、发型、服装和风格，只改变挥手动作与表情，然后直接生成并执行三层QA。

### Variant B

请重新选择人物方向、相似程度、风格和配色。

## Case: first-use-style-discovery

Prompt: 我第一次使用这个 Skill，上传了照片，帮我创建个人 IP。

Rubric:
- `all-styles-visible` (1.0): 首次使用能看到全部内置风格。
- `real-preview-contract` (1.0): 目录使用注册表正式预览而非只列名称。
- `capability-boundary` (1.0): 风格卡包含用途与验证边界。
- `selection-gate` (1.0): 未选择前停止且不生图。

### Variant A

未检测到风格偏好，默认使用软萌潮玩 Q 版并开始设计。

### Variant B

先分析人物参考，再真实展示两个内置风格的正式 catalog_preview：软萌潮玩 Q 版、像素角色设定风；每张卡片说明特点、适用用途、已验证与未验证产物，并标出一个有理由的推荐。随后停止，等待用户选择风格或回复‘采用推荐’；目录选择不等于人物方案确认或生图授权。
