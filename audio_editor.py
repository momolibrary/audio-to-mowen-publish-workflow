#!/usr/bin/env python3
"""
音频剪辑工具 - 去除静音空白，制作可发布版本
"""

from pydub import AudioSegment
from pydub.silence import detect_nonsilent, detect_silence
import os
import sys

def edit_audio(input_file, output_file, 
               min_silence_len=300,      # 最小静音长度(ms)才处理
               silence_thresh=-35,        # 静音阈值
               keep_silence=100,          # 保留的静音长度
               max_gap=500):              # 最大保留空白
    
    """
    编辑音频：去除过长静音，保留必要停顿
    """
    audio = AudioSegment.from_mp3(input_file)
    original_len = len(audio)
    
    print(f"原始时长: {original_len/1000:.1f}秒")
    
    # 检测非静音片段
    nonsilent_ranges = detect_nonsilent(
        audio, 
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    
    print(f"检测到 {len(nonsilent_ranges)} 个语音片段")
    
    # 构建新音频
    edited_audio = AudioSegment.empty()
    
    for i, (start, end) in enumerate(nonsilent_ranges):
        # 添加语音片段
        segment = audio[start:end]
        edited_audio += segment
        
        # 在片段之间添加适当的停顿
        if i < len(nonsilent_ranges) - 1:
            next_start = nonsilent_ranges[i+1][0]
            gap = next_start - end
            
            if gap > max_gap:
                # 过长空白，压缩到max_gap
                edited_audio += AudioSegment.silent(duration=max_gap)
            elif gap > keep_silence:
                # 中等空白，保留一部分
                edited_audio += AudioSegment.silent(duration=keep_silence)
            else:
                # 短空白，保留原样（加入一小段）
                edited_audio += AudioSegment.silent(duration=min(keep_silence, gap//2))
    
    edited_len = len(edited_audio)
    reduction = (original_len - edited_len) / original_len * 100
    
    print(f"编辑后时长: {edited_len/1000:.1f}秒")
    print(f"压缩: {reduction:.1f}%")
    
    # 导出
    edited_audio.export(output_file, format="mp3", 
                        parameters=["-ar", "16000", "-ac", "1"])
    
    return original_len, edited_len

def batch_edit(input_dir, output_dir):
    """批量处理所有音频"""
    mp3_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.mp3')])
    
    print(f"共 {len(mp3_files)} 个音频文件待处理\n")
    
    total_original = 0
    total_edited = 0
    
    for i, mp3_file in enumerate(mp3_files):
        print(f"\n[{i+1}/{len(mp3_files)}] {mp3_file}")
        
        input_path = os.path.join(input_dir, mp3_file)
        output_path = os.path.join(output_dir, mp3_file)
        
        try:
            orig, edit = edit_audio(input_path, output_path)
            total_original += orig
            total_edited += edit
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n\n=== 批量处理完成 ===")
    print(f"原始总时长: {total_original/60000:.1f}分钟")
    print(f"编辑总时长: {total_edited/60000:.1f}分钟")
    print(f"共压缩: {(total_original-total_edited)/60000:.1f}分钟")

if __name__ == "__main__":
    input_dir = "/Users/tecson/Downloads/tiedan/downloads/unpacked"
    output_dir = "/Users/tecson/Downloads/tiedan/downloads/edited"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 先测试单个文件
    print("=== 测试处理第一个音频 ===\n")
    test_file = "01月03日_1.mp3"
    edit_audio(
        os.path.join(input_dir, test_file),
        os.path.join(output_dir, test_file)
    )
