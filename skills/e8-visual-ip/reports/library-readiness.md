# Library 就绪说明

## 已验证

- `SKILL.md` 初始加载估算 `1145 / 1300` tokens，资源边界通过。
- 治理评分 `90 / 100`，声明的 `library` 层级通过且无警告。
- dev、holdout、blind holdout、adversarial 四组触发评测均无误触发与漏触发。
- 风格注册表覆盖 3 种内置风格和 15 个已登记资产；定义、引用、哈希和来源清单一致。
- 黑白风格运行契约已升级到 Schema 2.0：默认单张候选、`recognizable` 身份优先参考路由、五项身份指纹与身份／风格双硬门。
- 角色包生命周期、软萌潮玩契约、黑白运行契约、像素运行契约与 UTF-8 包完整性测试通过。
- Trust 检查通过：4 个 CLI 均有 help surface；无网络脚本、无密钥发现；唯一文件写入能力已限定到角色包边界并有季度复核日期。
- 输出契约为 7 个案例，包含 3 个 `file-backed fixture`；with-skill 断言通过率 100%，baseline 为 0%。
- 特朗普与 Sam Altman 的黑白失败模式已经进入回归：类别符号成立但脸部身份失败时，校验器禁止 `approved_candidate`。

## 仍为 missing evidence

- 不同模型上的真实生图 A/B。
- 尚未用重构后的 Schema 2.0 重新生成特朗普、Sam Altman 或其他人物，因此真实相似度提升仍为 `missing evidence`。
- 未见人物身份上的盲审相似度和风格还原度。
- 复杂场景、多人、长发黑白扩展、像素复杂动作等注册表中的 `unverified_outputs`。
- 参考图片的公开再分发授权；在复核前仅限本地内部使用。

## 发布边界

当前可作为中央 Library Skill 在链接项目中使用和继续测试，不应宣称已完成公开发行级视觉验证，也不应携带现有参考图对外分发。
