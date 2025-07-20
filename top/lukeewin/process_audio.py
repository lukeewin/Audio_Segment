# !/usr/bin/env python
# _*_ coding utf-8 _*_
# @Time: 2025/7/20 2:21
# @Author: Luke Ewin
# @Blog: https://blog.lukeewin.top
"""
处理音频格式为 pcm_s16le 单声道 16k 音频
"""
import os
import subprocess

# 指定输入和输出目录
input_dir = r'D:\Works\ASR\客家话\data\自己收集的数据集\整理好的数据\audio\myself'
output_dir = r'D:\Works\ASR\客家话\data\自己收集的数据集\整理好的数据\audio\test'

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历输入目录下的所有文件
for filename in os.listdir(input_dir):
    # 检查是否为音频文件
    if filename.endswith('.wav'):
        # 构建输入和输出文件路径
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')

        # 使用ffmpeg进行转码
        subprocess.call(['ffmpeg', '-i', input_path, '-ar', '16000', '-ac', '1', '-f', 'wav', '-acodec', 'pcm_s16le', output_path])
        print(f'Converted {filename} to {os.path.basename(output_path)}')
