# audio-to-mowen-publish-workflow

录音发布工作流：从讯飞听见导出录音，经 AI 处理后生成墨问格式的 shownotes。

## 功能

- 🎵 音频剪辑（自动去除静音）
- 📁 按组合并音频 + 生成时间轴
- 🔍 AI 内容校验（过滤不相关录音）
- 📝 剪映 SRT → 墨问 shownotes 自动生成
- 🔄 全流程参数化，支持多本书籍复用

## 工具链

```
讯飞听见 → 解压分离 → AI内容校验 → AI剪辑合并 → 剪映生成SRT → AI生成shownotes → 墨问发布
```

| 环节 | 工具 | 角色 |
|------|------|------|
| 下载 | 讯飞听见 | 录音来源 |
| 内容校验 | Claude | AI 自动 |
| 剪辑/合并 | Python (pydub) | AI 自动 |
| 字幕生成 | 剪映 | 人工操作 |
| shownotes 生成 | Claude | AI 自动 |
| 审核/发布 | 墨问 | 人工操作 |

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install pydub
```

### 2. 数据准备

将从讯飞听见导出的 zip 文件放入 `downloads/` 目录：

```bash
mkdir -p downloads
mv ~/Downloads/*.zip downloads/
```

### 3. 音频剪辑

```bash
python audio_editor.py
```

自动去除静音，输出到 `downloads/edited/`

### 4. 分组合并

编辑 `merge_groups.py` 中的 `GROUPS` 配置，然后运行：

```bash
# 使用默认配置
python merge_groups.py

# 自定义书名和起始序号
python merge_groups.py --book "书名" --start 1
```

输出到 `发布/{book_name}{序号}/`

### 5. 生成字幕（人工）

1. 打开剪映，导入合并后的 mp3
2. 使用"智能字幕" → "识别字幕"
3. 导出为 SRT 格式
4. 复制到对应分组目录

### 6. 生成 shownotes（AI）

基于 SRT 文件，AI 自动生成墨问格式的 shownotes：

```
HH:MM:SS 标题
正文内容（约500字/段）
```

### 7. 发布到墨问

人工审核后，将 shownotes 内容粘贴到墨问平台。

## 目录结构

```
audio-to-mowen-publish-workflow/
├── .gitignore              ← 忽略规则
├── README.md               ← 本文档
├── CLAUDE.md               ← 项目指引
├── WORKFLOW.md             ← 完整工作流（16步）
├── merge_groups.py         ← 合并脚本
├── audio_editor.py         ← 剪辑脚本
├── downloads/              ← 产物（已忽略）
│   ├── zips/               ← 原始 zip
│   ├── unpacked/           ← 解压后的 mp3 + docx
│   ├── audio/              ← mp3 副本
│   └── edited/             ← 剪辑后的版本
└── 发布/                   ← 产物（已忽略）
    └── {book_name}{序号}/
        ├── input/
        ├── {book_name}{序号}.mp3
        ├── {book_name}{序号}_时间轴.txt
        ├── {book_name}{序号}.srt
        └── {book_name}{序号}_shownotes.txt
```

## 墨问 shownotes 格式

```
00:00:00 章节标题
这里是正文内容，约500字段落...

00:05:30 下一个章节标题
继续正文内容...
```

- 时间戳：对应合并后音频的时间点
- 标题：5~15 字，新闻式风格
- 正文：每段约 500 字，基于 SRT 校对标点和错别字

## 注意事项

- 中文 zip 文件名需用 Python `zipfile` 解压，系统 `unzip` 会报编码错误
- 剪映导出的 SRT 文件名可能重复，需手动确认对应关系
- shownotes 生成前必须人工审核合并后的 mp3

## License

MIT
