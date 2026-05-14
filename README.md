# wechat-sticker-maker

一个 Claude Code Skill，用于将创意一站式转化为符合**微信表情开放平台**规范的完整素材包。从角色构思到 ZIP 提交包，全流程自动化。

## ✨ 功能特性

- 📐 **规范驱动**：内置 2024/2025 微信静态表情包官方规范
- 🎨 **智能生成**：内置中英文提示词模板，覆盖宫格图、横幅、赞赏图
- ✂️ **自动处理**：宫格图自动切割、智能裁剪、白底透明化
- ✅ **合规验证**：一键检查尺寸、格式、透明度，提示审核常见失败项
- 📦 **一键打包**：自动整理素材为可提交 ZIP

## 📁 项目结构

```
wechat-sticker-maker/
├── SKILL.md                  # 技能主文件（Claude 加载入口）
├── build.sh                  # 打包脚本，生成 .skill 文件
├── references/
│   └── wechat_specs.md       # 微信官方规范详表
├── scripts/
│   ├── sticker_processor.py  # 宫格切割 + 透明化处理
│   └── verify_package.py     # 合规验证
└── templates/
    └── prompt_templates.md   # 图像生成提示词模板
```

## 🚀 快速开始

### 安装为 Claude Skill

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/wechat-sticker-maker.git
cd wechat-sticker-maker

# 2. 打包为 .skill 文件
bash build.sh

# 3. 安装到 Claude（拖拽 wechat-sticker-maker.skill 到 Claude Code）
```

### 直接使用脚本

```bash
# 安装依赖
pip3 install Pillow numpy

# 处理宫格图（4×4 = 16 张表情）
python3 scripts/sticker_processor.py raw_grid.png ./output --grid 4x4

# 处理 24 张
python3 scripts/sticker_processor.py raw_grid.png ./output --grid 3x8

# 验证合规性
python3 scripts/verify_package.py ./output
```

## 🧩 完整工作流（5 步）

| 步骤 | 内容 | 工具 |
|------|------|------|
| 0 | 收集需求（角色、风格、数量） | 与用户对话 |
| 1 | 生成宫格图（4×4 或 3×8） | 图像生成模型 |
| 2 | 切割宫格为独立表情 + 透明化 | `sticker_processor.py` |
| 3 | 生成辅助素材（横幅/赞赏图） | 图像生成模型 |
| 4 | 合规验证 | `verify_package.py` |
| 5 | 打包 ZIP | `zip` 命令 |

完整工作流详见 [SKILL.md](./SKILL.md)。

## 📋 微信表情包规范速查

| 素材 | 尺寸 | 格式 | 数量 |
|------|------|------|------|
| 主图 | 240×240 | PNG（透明） | 16 或 24 |
| 缩略图 | 120×120 | PNG（透明） | 同主图 |
| 封面图 | 240×240 | PNG（透明） | 1 |
| 聊天面板图标 | 50×50 | PNG（透明） | 1 |
| 详情页横幅 | 750×400 | PNG/JPG | 1 |
| 赞赏引导图 | 750×560 | PNG/JPG | 1 |
| 赞赏致谢图 | 120×120 | PNG | 1 |

详见 [references/wechat_specs.md](./references/wechat_specs.md)。

## 🛠 脚本参数

### sticker_processor.py

```
python3 scripts/sticker_processor.py <input> <output_dir> [options]

参数：
  input              输入宫格图路径（PNG/JPG）
  output_dir         输出目录

可选：
  --grid 4x4|3x8     宫格布局（默认 4x4）
  --threshold 0-255  白色背景去除阈值（默认 245，越低越激进）
  --margin N         每格边缘裁剪像素（默认 8）
```

### verify_package.py

```
python3 scripts/verify_package.py <output_dir> [--count 16|24]
```

## 📦 依赖

- Python ≥ 3.8
- Pillow
- numpy

## 📄 License

MIT
