#!/usr/bin/env python3
"""
按分组方案合并 mp3 文件，生成时间轴
"""

import os
import shutil
from pydub import AudioSegment

# 分组定义
GROUPS = {
    "数学与艺术28": ["01月03日_1", "01月03日_2", "01月05日_2", "01月05日_3", "01月05日_4", "01月05日_5", "01月05日_6", "01月05日_7", "01月05日_8"],
    "数学与艺术29": ["01月07日_1", "01月07日_2", "01月09日_1"],
    "数学与艺术30": ["01月10日_1", "01月10日_2", "01月10日_3", "01月10日_4", "01月10日_5", "01月10日_6"],
    "数学与艺术31": ["01月18日_1", "01月18日_2", "01月25日_1", "01月25日_2"],
    "数学与艺术32": ["03月25日_1", "04月04日_1", "04月04日_2", "04月04日_3", "04月04日_4", "04月04日_5"],
    "数学与艺术33": ["04月05日_1", "04月05日_2", "04月05日_3", "04月06日_1", "04月06日_2", "04月06日_3", "04月06日_4"],
    "数学与艺术34": ["04月07日_1", "04月07日_2", "04月07日_3", "04月07日_4", "04月12日_1", "04月14日_1", "04月14日_2", "04月14日_3"],
    "数学与艺术35": ["04月23日_1", "06月01日_1", "06月01日_2", "06月01日_3", "06月01日_4"],
    "数学与艺术36": ["06月01日_5", "06月01日_6", "06月01日_7", "06月02日_1", "06月02日_2", "06月02日_3", "06月02日_4"],
    "数学与艺术37": ["06月04日_1", "06月04日_2"],
    "数学与艺术38": ["06月05日_1", "06月06日_1", "06月06日_2", "06月06日_3", "06月06日_4", "06月06日_5", "06月06日_6"],
    "数学与艺术39": ["06月06日_7", "06月06日_8", "06月06日_9", "06月06日_10", "06月06日_11", "06月06日_12", "06月06日_13", "06月06日_14", "06月06日_15", "06月06日_16"],
}

EDITED_DIR = "downloads/edited"
OUTPUT_DIR = "发布"


def format_time(ms):
    """毫秒转 HH:MM:SS 格式"""
    total_sec = ms / 1000
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def merge_group(group_name, files):
    """合并一组文件"""
    group_dir = os.path.join(OUTPUT_DIR, group_name)
    input_dir = os.path.join(group_dir, "input")
    os.makedirs(input_dir, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"处理: {group_name}")
    print(f"{'='*50}")

    # 1. 复制输入文件到 input/
    for name in files:
        for ext in [".mp3", ".docx"]:
            src = os.path.join(EDITED_DIR, name + ext)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(input_dir, name + ext))
                print(f"  复制: {name}{ext}")

    # 2. 合并 mp3 并生成时间轴
    merged = AudioSegment.empty()
    timeline_lines = []

    for name in files:
        mp3_path = os.path.join(EDITED_DIR, name + ".mp3")
        if not os.path.exists(mp3_path):
            print(f"  ⚠️ 缺失: {name}.mp3")
            continue

        audio = AudioSegment.from_mp3(mp3_path)
        start_time = format_time(len(merged))
        duration_sec = len(audio) / 1000

        merged += audio
        end_time = format_time(len(merged))

        timeline_lines.append(f"{start_time} - {end_time}  {name}（{duration_sec/60:.1f}分钟）")
        print(f"  合并: {name} ({duration_sec/60:.1f}分) @ {start_time}")

    # 3. 导出合并后的 mp3
    output_mp3 = os.path.join(group_dir, f"{group_name}.mp3")
    merged.export(output_mp3, format="mp3", parameters=["-ar", "16000", "-ac", "1"])
    print(f"  ✅ 导出: {output_mp3} ({len(merged)/60000:.1f}分钟)")

    # 4. 保存时间轴
    timeline_path = os.path.join(group_dir, f"{group_name}_时间轴.txt")
    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write(f"# {group_name} 时间轴\n")
        f.write(f"# 总时长: {format_time(len(merged))}\n\n")
        for line in timeline_lines:
            f.write(line + "\n")
    print(f"  ✅ 时间轴: {timeline_path}")

    return len(merged)


def main():
    total_ms = 0
    for group_name, files in GROUPS.items():
        duration = merge_group(group_name, files)
        total_ms += duration

    print(f"\n{'='*50}")
    print(f"全部完成！总时长: {format_time(total_ms)}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
