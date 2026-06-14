# CLAUDE.md — 项目指引

## 项目简介
从讯飞听见平台批量导出朗读录音，经过剪辑、分组、字幕、shownotes 生成，最终发布。

## 关键路径
- 工作流文档：`WORKFLOW.md`
- 进度追踪：`工作进展.md`
- 合并脚本：`merge_groups.py`
- 剪辑脚本：`audio_editor.py`

## 目录约定
- 原始文件放 `downloads/`（zips/ unpacked/ audio/ edited/）
- 发布产出放 `发布/数学与艺术XX/`
- 每组包含：input/、合并mp3、时间轴、SRT、shownotes

## 技术要点
- 中文 zip 必须用 Python `zipfile` 解压
- 音频剪辑用 `pydub`，在 `.venv` 环境中运行
- SRT 用剪映手动导出，放到 `~/Downloads/` 后复制到项目
- shownotes 按 ~500 字分段，每段带时间戳 + 新闻式标题

## 命名规范
- 分组标题：`数学与艺术{序号}`（接续已发布内容）
- 文件名：`数学与艺术XX.mp3`、`数学与艺术XX_shownotes.txt`
