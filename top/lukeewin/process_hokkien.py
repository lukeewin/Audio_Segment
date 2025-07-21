# !/usr/bin/env python
# _*_ coding utf-8 _*_
# @Time: 2025/7/21 16:13
# @Author: Luke Ewin
# @Blog: https://blog.lukeewin.top
"""
处理从 huggingface 中下载的闽南语 cvs 为符合 funasr 训练的格式
"""


def process_cvs(cvs_file: str, save_scp: str, save_txt: str):
    i = 0
    with open(cvs_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 获取最后一个逗号前的内容
            tmp = line.strip().split(',', -1)
            audio_path = tmp[-1]
            content = tmp[0]
            with open(save_scp, 'a', encoding='utf-8') as w:
                w.write(f"{i} {audio_path}\n")
            with open(save_txt, 'a', encoding='utf-8') as t:
                t.write(f"{i} {content}\n")
            i += 1

# cvs_file = r"E:\train_data\Hokkien\metadata.csv"
# save_scp = r"E:\train_data\Hokkien\train_wav.scp"
# save_txt = r"E:\train_data\Hokkien\train_text.txt"
# process_cvs(cvs_file, save_scp, save_txt)


def generate(text_file: str, save: str, type: str):
    """
    根据输入的 train_text.txt 文件生成 train_text_language.txt train_emo.txt train_event.txt
    :param text_file: 输入的 train_text.txt
    :param save: 保存文件
    :param type: 类型
    :return:
    """
    with open(text_file, 'r', encoding='utf-8') as r:
        lines = r.readlines()

    with open(save, 'w', encoding='utf-8') as w:
        for line in lines:
            tmp = line.strip().split(' ', 1)
            uuid = tmp[0]
            content = tmp[-1]
            if content is not None:
                w.write(f"{uuid} {type}\n")


text_file = r"E:\train_data\Hokkien\val_text.txt"
save = r"E:\train_data\Hokkien\val_emo.txt"
type = "<|NEUTRAL|>"
generate(text_file, save, type)
