# 内置风格目录

本目录用于首次风格发现，不替代风格定义。所有信息从 `style-registry.json` 读取；只展示同时满足 `lifecycle_status: active` 与 `catalog_visible: true` 的条目，过滤后的注册表顺序就是用户看到的编号。

## 展示条件

- 首次创建人物且用户没有指定风格：必须展示。
- 用户询问“有哪些风格”“风格有什么区别”：只展示目录，不要求先上传照片。
- 用户已经明确指定内置风格：不重复展示。
- 用户提供新的风格参考：进入比较或自定义风格流程。
- 用户明确说“你帮我选”：可以直接推荐，但仍展示被选中的正式预览和理由。

## 展示协议

逐个读取注册表条目的：

- `lifecycle_status`
- `catalog_visible`
- `display_name`
- `catalog_preview`
- `catalog_primary_style`
- `catalog_summary`
- `catalog_best_for`
- `supported_outputs`
- `unverified_outputs`

使用当前环境的图片查看或展示能力真实展示 `catalog_preview`。若环境不能显示本地图片，必须明确说明预览不可见，并提供风格名称、摘要和相对路径；不得声称用户已经看过图片。

`candidate` 和 `deprecated` 风格禁止进入目录、编号和自动推荐；只有用户明确点名候选风格并要求校准时，才能进入对应候选工作流。

每个风格使用以下短卡片：

```text
风格 N：<display_name>
<真实预览图>
特点：<catalog_summary>
适合：<catalog_best_for>
已验证：<supported_outputs>
暂未验证：<unverified_outputs>
```

结合用户的人物参考与用途，在一个风格名称后标注“推荐”，并用一句具体理由解释。不得用“最好看”“最高级”等空话。

目录末尾只问：

> 请选择一个风格，或回复“采用推荐”。这一步只确定画法，还不会开始生成。

## 预览一致性

- 用户根据目录选择风格时，注册表中的 `catalog_primary_style` 成为默认 `primary style`。
- `catalog_primary_style` 必须与 `catalog_preview` 相同，或是从该预览图登记产生的正面裁图；不得来自另一套人物或画法。
- 内部存在多张参考图时，不得因为身份特征而静默替换目录画法。
- 若另一张内部参考明显更适合，必须先展示差异并获得用户同意。
- 目录预览与默认生成主参考必须具有可追溯的同源关系；`plan.md`、Prompt 和图片工具调用中的 `primary style` 必须一致使用 `catalog_primary_style`。
