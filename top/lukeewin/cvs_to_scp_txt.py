# !/usr/bin/env python
# _*_ coding utf-8 _*_
# @Time: 2025/7/19 14:54
# @Author: Luke Ewin
# @Blog: https://blog.lukeewin.top
"""
生成 FunASR 训练中要求的输入格式 scp 和 txt 文件
scp 格式如下：
序号 音频路径
txt 格式如下：
序号 音频对应的文本
"""


def generate(cvs_file: str, save_scp: str, save_txt: str):
    i = 0
    with open(cvs_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 获取第一个空格前的内容
            tmp = line.strip().split(' ', 1)
            audio_path = tmp[0]
            content = tmp[-1]
            with open(save_scp, 'a', encoding='utf-8') as w:
                w.write(f"{i} {audio_path}\n")
            with open(save_txt, 'a', encoding='utf-8') as t:
                t.write(f"{i} {content}\n")
            i += 1


cvs_file = r"D:\Works\ASR\客家话\data\自己收集的数据集\整理好的数据\segment_all.csv"
save_scp = r"D:\Works\ASR\客家话\data\自己收集的数据集\整理好的数据\train.scp"
save_txt = r"D:\Works\ASR\客家话\data\自己收集的数据集\整理好的数据\train.txt"
generate(cvs_file, save_scp, save_txt)
