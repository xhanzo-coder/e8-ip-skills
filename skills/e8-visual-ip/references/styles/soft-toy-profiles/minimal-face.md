---
id: minimal-face
parent_style: soft-toy-chibi
display_name: 极简五官软糯贴纸路线
reference_asset: ../../../assets/style-references/soft-toy-chibi/minimal-face-sheet.png
---

# Minimal Face Prompt Profile

## 适用范围

用于五官适合高度简化、气质克制、希望紧凑可爱或需要稳定三视图的个人角色。该路线不是普通“Q版动漫”，而是带生活方式气质的二维超变形角色设定。

此 Profile 覆盖 `soft-toy-chibi.md` 中较宽泛的比例、脸部、线条、渲染与三视图表达；身份锚点、服装身份和招牌系统仍来自用户本人。

## 风格固定项

### 比例与体块

- 约 2.7～3 个头高。
- 头部和发型体积明显大，脸型接近横向圆角胶囊。
- 耳朵适度外凸，脖子极短或基本隐藏。
- 肩膀窄、躯干紧凑、四肢短小。
- 服装轮廓柔软、圆润、略膨胀；不能显露成人胸腰胯。
- 手脚图形化，鞋型厚实圆润。

### 五官

- 眼睛使用极小竖向豆豆眼、短线眼或同等信息量的极简眼型。
- 嘴巴很小且闭合，鼻部省略。
- 腮红为清楚圆形或柔和椭圆，主要位于双颊；耳朵可有少量同色 blush。
- 表情害羞、平静、友好或轻微呆萌，不使用玻璃虹膜、长睫毛、牙齿和成熟妆感。

### 线条

- 外轮廓使用暖深棕，不使用冷纯黑。
- 外轮廓视觉重量约为内部线的 1.8～2.2 倍。
- 外轮廓闭合、圆润，连接处柔和；允许极轻微手绘弹性。
- 内部线数量克制，局部可以开放，不逐条刻画头发、缝线和鞋底纹理。
- 禁止统一粗细的矢量描边和细黑动漫线稿。

### 上色与光影

- 约 75%～85% 视觉面积使用稳定平涂。
- 每个主要色块最多一层局部阴影，阴影颜色来自本地色，边缘清楚但不过度锐利。
- 帽子、头发、外套或鞋子只允许少量小型柔和高光。
- 柔和渐变主要用于脸颊和耳朵，不对全身使用气枪渐变。
- 禁止半厚涂、写实材质、塑料3D和全局柔光。

### 三视图呈现

- 横向画布，正面、可读侧面或四分之三侧面、背面。
- 三个人物等高、同基线、间距一致。
- 头身比、头发体积、耳朵大小、服装长度、配饰位置和鞋型在各视角保持一致。
- 纯白背景，无文字、无标签、无地面阴影和场景。
- 白色贴纸 halo 是可选 `sticker-outline` 呈现，不是人物风格必需项；启用时只能是窄白边和极细浅灰外缘。

## 身份与示例内容分离

参考图中的男孩、海军蓝帽子、浅黄徽标、棕色短发、橄榄色连帽衫、橙色围巾、橙色短裤和具体鞋型仅用于校准原参考，不得默认迁移给用户。

生成用户角色时必须替换：

- 性别、年龄与气质。
- 用户自己的发型和发色。
- 用户是否佩戴眼镜、帽子和耳饰。
- 角色化服装、身份色和招牌系统。
- 是否需要贴纸白边。

必须保留的只是比例、胶囊脸、极简五官、线条层级、圆润体块、有限阴影和三视图一致性。

## 参考校准 Prompt

仅用于验证 `minimal-face-sheet.png` 本身能否被稳定复现，禁止用于生成其他用户角色：

```text
Use the attached reference image as the primary and dominant guide for proportions, shape language, line hierarchy, rendering, palette organization, and turnaround layout.

Create a horizontal three-view model sheet in a 2D super-deformed lifestyle mascot style, not a mainstream anime illustration. Show the exact same original chibi boy in three evenly spaced, equal-height full-body views on one shared baseline: front view, left-facing readable three-quarter side view, and back view.

Use approximately 2.7–3 head-tall proportions: oversized head and cap, wide rounded capsule-like face, prominent ears, almost no visible neck, narrow shoulders, compact torso, short limbs, tiny simplified hands, and chunky rounded shoes. Clothing forms soft inflated silhouettes and hides realistic anatomy.

Line language: warm dark-brown outer contours approximately 1.8–2.2 times the visual weight of interior lines; rounded joins, slight hand-drawn elasticity, clean closed outer silhouettes, and sparse simplified interior details. Avoid uniform vector outlines and thin cold-black anime line art.

Rendering: 75%–85% stable flat local colors, one simple local-color shadow layer with clear but not razor-sharp edges, and only a few small restrained highlights on the cap, hair, hoodie, and shoes. Use soft gradients mainly on cheeks and ears. No global airbrush gradients, painterly rendering, realistic volume lighting, plastic 3D shading, or complex material texture.

Face: tiny vertical black eyes, very small closed mouth, no visible nose, large circular rosy cheeks, shy and calm neutral-cute expression. No detailed iris, long eyelashes, teeth, glass-eye highlights, or mature facial features.

Character calibration: navy baseball cap with a pale yellow oval badge and small top button; short softly wavy brown hair; light peach skin; oversized olive hoodie with rounded hood and front kangaroo pocket; orange scarf or high collar; orange knee-length shorts with narrow cream side stripes; cream socks; chunky cream sneakers with small muted-blue patches.

Color hierarchy: olive is the largest clothing color, orange is the main accent, navy is concentrated on the cap, cream is used for shoes and small highlights, and peach/pink is limited to skin and blush. Keep the palette muted, warm, and cohesive.

Turnaround consistency: preserve identical head-to-body ratio, cap size, badge placement, hair volume, ear size, facial proportions, hoodie length, hood shape, pocket placement, scarf height, shorts length, stripe positions, sock height, shoe construction, and palette across all three views.

Presentation: clean pure-white background, no floor shadow, scenery, text, labels, or decorative elements. Use only a subtle narrow white sticker halo with a very thin pale-gray outer keyline.

Avoid realistic proportions, long limbs, adult waist or hips, mainstream anime eyes, thin uniform outlines, strong global gradients, excessive gloss, painterly or 3D rendering, inconsistent views, different characters across views, and single-pose composition.
```

## 用户生产 Prompt 模板

```text
Image 1 is the dominant minimal-face style reference. It controls the 2.7–3 head-tall proportions, capsule-like face, tiny vertical eyes, rounded soft body shapes, warm dark-brown line hierarchy, flat-color rendering, restrained local shadows, and character-sheet presentation. Image 2 is identity reference only and must not control realistic anatomy, adult proportions, rendering medium, or the exact photo pose.

Create one reusable personal chibi character using the user identity specification below.

Identity anchors: {2–5 stable user features}.
Character direction: {recognizable / interpreted / symbolic}.
Hair: {user hair silhouette and color, simplified into large rounded blocks}.
Face: wide rounded capsule-like face, {user-specific brow/eye temperament} translated into tiny vertical or short-line eyes, tiny closed mouth, no visible nose, and clear rounded cheek blush.
Outfit identity: {user outfit category} redesigned as soft, rounded, slightly inflated character shapes with narrow shoulders, compact torso, short limbs, minimal seams, and chunky rounded footwear.
Palette: {one dominant color, one or two supporting colors, one accent carrier, skin/hair neutrals}; muted, warm, cohesive, and clearly prioritized.
Signature system: {zero to two user-specific accessories or symbols}; do not copy the reference boy’s cap, badge, scarf, hoodie, shorts, shoes, gender, or palette unless independently required by the user identity.

Line language: warm dark-brown closed outer contours 1.8–2.2 times heavier than sparse interior lines, rounded joins, slight hand-drawn elasticity, no uniform vector outline and no thin cold-black anime line art.

Rendering: 75%–85% stable flat local colors; maximum one local-color shadow layer per major shape; a few small restrained highlights; soft gradients mainly on cheeks and ears; no painterly rendering, global airbrush gradient, realistic lighting, material texture, or 3D plastic look.

Output mode: {single front base character / horizontal front–three-quarter-side–back turnaround}.
For turnaround: same character, equal height, shared baseline, even spacing, identical proportions, hair mass, face, outfit construction, accessory positions, shoe shape, and palette across all views.
Sticker outline: {off by default / narrow white halo with very thin pale-gray outer keyline}.
Background: pure white, no floor shadow, scenery, text, labels, or decoration.

Avoid realistic anatomy, adult waist and hips, long limbs, detailed anime iris, long eyelashes, teeth, thin uniform outlines, strong gradients, excessive gloss, painterly/3D rendering, photo pose copying, reference-character contamination, and inconsistent views.
```

## Minimal Face 专属 QA

- 头身比位于约 2.7～3，不能超过 3.2。
- 脸型横向圆润，耳朵外凸，脖子极短。
- 眼睛是竖向豆豆眼、短线眼或同等信息量，不得出现详细虹膜。
- 嘴巴极小、闭合，鼻子不可见，双颊有明确腮红。
- 外轮廓为暖深棕，明显重于内部线。
- 平涂占主体，每个主要色块最多一层阴影和少量高光。
- 服装必须是柔软膨胀体块，不能呈现成人身体结构。
- 贴纸白边只在 `sticker-outline` 开启时出现。
- 三视图必须等高、同基线，并保持所有结构、配饰和色板一致。
- 任何参考男孩的具体服装、帽子、徽标、性别或配色迁移到无关用户时，直接失败。
