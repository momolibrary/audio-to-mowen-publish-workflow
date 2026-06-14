# 录音发布工作流

本文档记录从录音原始文件到可发布 shownotes 的完整工作流，适用于后续批次复用。

## 总览

```
原始 zip → 解压分离 → 音频剪辑 → 分组合并 → 生成字幕 → 生成 shownotes → 发布
```

## 阶段一：数据采集与归档

### 1. 下载原始文件
- 从讯飞听见平台批量导出 zip 文件
- 每个 zip 包含一个 `.mp3`（录音）和一个 `.docx`（转写文本）

### 2. 移动到项目目录
```bash
mv ~/Downloads/*.zip downloads/
```

### 3. 解压与分离
用 Python 解压（避免系统 unzip 的中文编码问题）：
```python
import zipfile, os, glob
for z in sorted(glob.glob('downloads/*.zip')):
    with zipfile.ZipFile(z, 'r') as zf:
        for name in zf.namelist():
            target = os.path.join('downloads/unpacked', os.path.basename(name))
            with zf.open(name) as src, open(target, 'wb') as dst:
                dst.write(src.read())
```

### 4. 归档整理
```bash
mkdir -p downloads/{zips,unpacked,audio,edited}
mv downloads/*.zip downloads/zips/
cp downloads/unpacked/*.mp3 downloads/audio/
```

### 5. 数据清洗
- 检查 docx 内容，排除非朗读文件（如平台提示信息）
- 校验 zip / unpacked / audio 三方数量一致

## 阶段二：音频剪辑

### 6. 批量剪辑
使用 `audio_editor.py` 对所有 mp3 进行静音去除：
- 输入：`downloads/unpacked/*.mp3`
- 输出：`downloads/edited/*.mp3` + 对应 docx
- 依赖：`pydub`（需在 `.venv` 中安装）

```bash
.venv/bin/python3 audio_editor.py
```

剪辑参数：
- 静音阈值：-35 dB
- 最小静音长度：300ms
- 保留静音：100ms
- 最大空白：500ms

## 阶段三：分组规划

### 7. 按日期归集
- 按录制日期分组，每组 30~60 分钟
- 优先连续日期归为一组
- 命名格式：`数学与艺术{序号}`（序号接续已发布内容）

### 8. 创建分组定义
在 `merge_groups.py` 中定义 `GROUPS` 字典：
```python
GROUPS = {
    "数学与艺术28": ["01月03日_1", "01月03日_2", ...],
    "数学与艺术29": ["01月07日_1", ...],
    ...
}
```

### 9. 生成合并音频与时间轴
```bash
.venv/bin/python3 merge_groups.py
```

输出目录结构：
```
发布/
├── 数学与艺术XX/
│   ├── input/                    ← 原始 mp3 + docx
│   ├── 数学与艺术XX.mp3          ← 合并音频
│   └── 数学与艺术XX_时间轴.txt    ← 每段起止时间
```

## 阶段四：字幕生成（人工 + 工具）

### 10. 剪映生成字幕
1. 打开剪映，导入合并后的 mp3
2. 使用"智能字幕" → "识别字幕"
3. 导出为 SRT 格式，保存到 `~/Downloads/`
4. 复制到对应分组目录：
   ```bash
   cp ~/Downloads/xxx.srt "发布/数学与艺术XX/数学与艺术XX.srt"
   ```

## 阶段五：Shownotes 生成

### 11. 解析 SRT 与合并段落
将 SRT 按约 500 字合并为段落：
```python
def merge_segments(items, target=500):
    segments = []
    buf, buf_len, start_time = [], 0, None
    for item in items:
        if not buf:
            start_time = item['start']
        buf.append(item['text'])
        buf_len += len(item['text'])
        if buf_len >= target:
            segments.append({'time': start_time, 'text': ''.join(buf)})
            buf, buf_len = [], 0
    if buf:
        segments.append({'time': start_time, 'text': ''.join(buf)})
    return segments
```

### 12. 生成标题与校对正文
对每段执行：
- **生成标题**：5~15 字，新闻式风格，反映核心内容
- **校对正文**：仅修正标点和错别字，不删改内容

参考工具：`/Users/tecson/Documents/github/kimi-srt2shownotes/main.py`
- 可用 Kimi API 自动化
- 也可用 Claude 直接处理

### 13. 输出格式
```
HH:MM:SS 标题
正文内容

HH:MM:SS 标题
正文内容
...
```

保存为 `发布/数学与艺术XX/数学与艺术XX_shownotes.txt`

## 阶段六：更新进度

### 14. 更新工作进展
在 `工作进展.md` 的进度表中，将对应组的状态标记为 ✅。

## 目录结构总览

```
tiedan/
├── downloads/
│   ├── zips/          ← 原始 zip 归档
│   ├── unpacked/      ← 解压后的原始 mp3 + docx
│   ├── audio/         ← mp3 副本
│   ├── edited/        ← 剪辑后的可发布版本
│   └── transcript/    ← 转写文本
├── 发布/
│   ├── 数学与艺术28/
│   │   ├── input/
│   │   ├── 数学与艺术28.mp3
│   │   ├── 数学与艺术28_时间轴.txt
│   │   ├── 数学与艺术28.srt
│   │   └── 数学与艺术28_shownotes.txt
│   └── ...
├── merge_groups.py     ← 合并脚本
├── audio_editor.py     ← 剪辑脚本
├── 工作进展.md          ← 分组方案与进度追踪
└── WORKFLOW.md          ← 本文档
```

## 关键脚本

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `audio_editor.py` | 批量去除静音 | pydub |
| `merge_groups.py` | 按组合并 mp3 + 生成时间轴 | pydub |

## 注意事项

- 中文 zip 文件名需用 Python `zipfile` 解压，系统 `unzip` 会报编码错误
- 剪映导出的 SRT 文件名可能重复（如 `6月14日 (1).srt`），需手动确认对应关系
- shownotes 生成前必须人工审核合并后的 mp3
- 每组 shownotes 的时间戳对应合并后音频的时间，非原始文件时间
