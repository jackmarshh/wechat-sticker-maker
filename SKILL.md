---
name: wechat-sticker-maker
description: 制作符合微信表情商店规范的完整静态表情包素材包。从创意概念到可提交ZIP包，覆盖表情生成、智能裁剪、透明化处理、辅助素材生成及合规打包全流程。当用户想制作、设计微信表情包时触发。
---

# 微信表情包制作技能 (WeChat Sticker Maker)

当用户想制作微信表情包（静态）提交至微信表情开放平台时使用本技能。完整流程分为 5 步。

---

## Step 0：收集用户需求

开始前，**必须**向用户确认以下信息（未提供则追问）：

| 信息 | 说明 | 默认值 |
|------|------|--------|
| **角色/主题** | 表情的主角，如"一只橙色柴犬"、"穿西装的螃蟹" | 无默认，必填 |
| **风格** | Q版卡通 / 水彩 / 像素风 / 扁平插画 | Q版卡通 |
| **数量** | 16 张（4×4 宫格）或 24 张（3×8 宫格）| 16 张 |
| **项目名称** | 用于命名输出文件夹和 ZIP 包 | `my_stickers` |
| **赞赏引导语** | 5-15 个字，如"感谢支持，爱你哦！" | 可在 Step 3 后确定 |

---

## Step 1：生成表情合集图

使用图像生成工具，**一次**生成包含全部表情的宫格图，保存为 `raw_grid.png`。

### 提示词模板（英文效果更好）

**16 张（4×4 宫格）：**
```
A clean 4x4 grid of 16 unique [CHARACTER DESCRIPTION] cartoon sticker expressions,
pure white background, thick black outline, Q-version chibi style, consistent character design,
equal cell spacing with visible grid, 16 different emotions including:
happy, sad, angry, surprised, winking, sleeping, thinking, eating,
running, dancing, crying, laughing, cool with sunglasses, waving, heart eyes, thumbs up.
Each sticker clearly separated, no overlapping.
```

**24 张（3×8 宫格）：**
```
A clean 3x8 grid (3 rows, 8 columns) of 24 unique [CHARACTER DESCRIPTION] cartoon sticker expressions,
pure white background, thick black outline, Q-version chibi style, consistent character design,
equal cell spacing with visible grid, 24 different emotions:
happy, sad, angry, surprised, winking, sleeping, thinking, eating,
running, dancing, crying, laughing, cool with sunglasses, waving, heart eyes, thumbs up,
shy, excited, bored, confused, celebrating, sick, working, greeting.
Each sticker clearly separated, no overlapping.
```

**关键提示词要求（勿省略）：**
- `pure white background` — 背景去除的前提
- `thick black outline` — 轮廓检测质量保证
- `consistent character design` — 跨格风格统一
- `equal cell spacing with visible grid` — 裁剪精度保证

---

## Step 2：处理宫格图为独立表情

确保已安装依赖：
```bash
pip3 install Pillow numpy
```

运行处理脚本：
```bash
# 16 张（4×4）
python3 scripts/sticker_processor.py raw_grid.png ./output_package --grid 4x4

# 24 张（3×8）
python3 scripts/sticker_processor.py raw_grid.png ./output_package --grid 3x8
```

**脚本自动生成：**
```
output_package/
├── main/
│   ├── sticker_01.png  (240×240px, 透明背景)
│   ├── sticker_02.png
│   └── ... (共 16 或 24 张)
├── thumbnail/
│   ├── thumb_01.png    (120×120px, 透明背景)
│   └── ...
├── panel_icon.png      (50×50px, 透明背景)
└── cover.png           (240×240px, 透明背景，取第1张)
```

**常见问题排查：**
- 背景未完全透明 → 原图背景非纯白，需重新生成或调整脚本阈值参数 `--threshold 245`
- 表情被裁剪 → 宫格间距不均，重新生成时在提示词中加强 `equal cell spacing`
- 脚本报错 → 检查 Python 版本（需 ≥ 3.8）和依赖安装

---

## Step 3：生成辅助素材

**必须一批次生成所有辅助素材**以保证风格统一。每张都需要与主角风格一致。

### 3a. 详情页横幅 (banner.png)
- **尺寸**：750×400 px
- **要求**：丰富背景场景，展示主角，**无文字**
- **提示词**：
  ```
  [CHARACTER] in a [SCENE/SETTING], banner illustration, 750x400 pixels aspect ratio,
  no text, vibrant colorful background, [STYLE], promotional banner style
  ```
- 保存为 `output_package/banner.png`

### 3b. 赞赏引导图 (appreciation_guide.png)
- **尺寸**：750×560 px
- **要求**：温馨插画，引导用户赞赏
- **提示词**：
  ```
  [CHARACTER] cute warm appreciation illustration, 750x560 pixels aspect ratio,
  soft warm colors, heartwarming cozy scene, [STYLE], no text overlay
  ```
- 保存为 `output_package/appreciation_guide.png`

### 3c. 赞赏致谢图 (appreciation_thanks.png)
- **尺寸**：120×120 px
- **要求**：角色表达感谢
- **提示词**：
  ```
  [CHARACTER] grateful thank you expression, chibi [STYLE], 120x120 pixels,
  white background, thick black outline, simple clean design
  ```
- 保存为 `output_package/appreciation_thanks.png`

### 3d. 赞赏引导语
在 `output_package/appreciation_text.txt` 中写入 5-15 字引导语，例如：
- `感谢支持，爱你哦！`
- `你的打赏是我创作的动力~`
- `买杯咖啡给作者充充电吧！`

---

## Step 4：合规检查

运行验证脚本检查所有素材是否符合微信规范：
```bash
python3 scripts/verify_package.py ./output_package
```

所有检查项通过后继续下一步。若有不符合项，按提示修复。

---

## Step 5：打包 ZIP

```bash
PROJECT_NAME="my_stickers"  # 替换为实际项目名

cd output_package
zip -r ../${PROJECT_NAME}.zip .
cd ..

echo "✓ 打包完成：${PROJECT_NAME}.zip"
```

**最终文件结构验证：**
```
my_stickers.zip
├── main/sticker_01.png ~ sticker_16.png
├── thumbnail/thumb_01.png ~ thumb_16.png
├── panel_icon.png
├── cover.png
├── banner.png
├── appreciation_guide.png
├── appreciation_thanks.png
└── appreciation_text.txt
```

---

## 规范速查

详细规范见 `references/wechat_specs.md`。

| 素材 | 尺寸 | 格式 | 数量 |
|------|------|------|------|
| 主图 | 240×240 | PNG（透明） | 16 或 24 |
| 缩略图 | 120×120 | PNG（透明） | 同主图 |
| 封面图 | 240×240 | PNG（透明） | 1 |
| 聊天面板图标 | 50×50 | PNG（透明） | 1 |
| 详情页横幅 | 750×400 | PNG/JPG | 1 |
| 赞赏引导图 | 750×560 | PNG/JPG | 1 |
| 赞赏致谢图 | 120×120 | PNG | 1 |
