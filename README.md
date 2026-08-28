# E8 IP Skills

面向个人视觉 IP 的 Agent Skills 套件。仓库采用一个 Git 仓库管理多个可独立安装的 Skill，并通过公开的角色包协议保持人物身份、风格与下游视觉资产一致。

> 当前状态：开源初始版本。Skill 流程与结构测试已经通过；真实视觉质量仍按各风格的 `unverified_outputs` 和质量报告如实标注。

[English](README.en.md)

## Skills

| Skill | 状态 | 职责 |
|---|---|---|
| `e8-visual-ip` | 开发中 | 创建、确认、保存、修改、审计和复用个人视觉 IP 角色 |
| `e8-ip-article-illustrator` | 规划中 | 读取正式角色包，为文章规划并生成保持人物一致的插图 |

每个 `skills/<name>/` 目录必须能够脱离仓库其他 Skill 独立运行。Skill 之间不得通过 `../../skills/<name>` 读取兄弟目录。

## 当前能力

`e8-visual-ip` 当前支持：

- 从照片、文字或已有角色建立基础人物；
- 首次使用时展示内置风格目录；
- 区分身份参考与风格参考；
- 创建正面母图、三视图、头像及已验证的衍生资产；
- 新增自定义风格；
- 检查人物漂移、风格漂移并修复候选；
- 将正式人物保存为跨 Skill 复用的角色包。

部分能力仍处于 `unverified_outputs`，以各 Skill 的注册表和 `SKILL.md` 为准，不因出现在路线图中就视为稳定功能。

## 安装

仓库公开后，计划支持按需安装，而不是强制加载全部 Skills：

```bash
npx skills add xhanzo-coder/e8-ip-skills
```

也可以只把某个完整 Skill 目录复制或链接到项目：

```text
<project>/.agents/skills/e8-visual-ip/
```

仓库地址：[github.com/xhanzo-coder/e8-ip-skills](https://github.com/xhanzo-coder/e8-ip-skills)

## 最小使用示例

```text
使用 $e8-visual-ip，根据我上传的照片创建个人视觉 IP。
如果我没有指定风格，先展示全部内置风格预览供我选择。
```

普通“帮我创建个人 IP”只授权分析和提案，不授权立即生图。正式人物和新增风格必须经过用户明确确认。

## 角色包协议

`e8-visual-ip` 是正式角色包的唯一写入方。文章配图、封面、视频等后续 Skills 只读角色包，不得静默改变人物基准。

```text
.creator-space/visual-ip/characters/<character-key>/
├── manifest.json
├── character.md
├── refs/
└── styles/
```

下游 Skill 没有角色包时应允许用户直接提供正式人物图，但必须明确跨图一致性会降低。详细边界见 [架构说明](docs/architecture.md)。

## 验证

仓库级验证只使用 Python 标准库：

```bash
python scripts/validate_all.py
```

验证内容包括：

- UTF-8 无 BOM；
- JSON 与 JSONL 可解析；
- Skill 名称、目录和 frontmatter；
- 每个 Skill 自带的结构、Schema、生命周期与回归测试；
- 禁止将本机绝对路径写入可公开文本。

## 隐私与生成结果

以下内容不得提交：

- `.creator-space/`；
- 用户照片、证件照和个人角色包；
- `visual-ip/`、`outputs/` 和普通生成结果；
- Cookie、Token、API Key、`.env` 和登录状态；
- 本机临时目录和绝对路径报告。

## 发布质量规则

- 使用合规的合成人物或已授权素材完成三个风格的真实视觉回归；
- 清除私人路径、个人照片和本地运行状态；
- 在干净环境中分别安装并运行每个 Skill；
- 完成人工视觉审查，不能用文本断言代替真实出图质量。

## 许可证

仓库代码、Skill 文本及 [资产权属清单](skills/e8-visual-ip/assets/provenance.json) 中已确认的图片采用 [MIT License](LICENSE)。图片授权说明见 [ASSET_LICENSE.md](ASSET_LICENSE.md)。
