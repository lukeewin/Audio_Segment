#!/usr/bin/env python
# _*_ coding utf-8 _*_
# @Time: 2025/7/6 15:47
# @Author: Luke Ewin
# @Blog: https://blog.lukeewin.top
import ffmpeg
import pysrt
import os
import glob


def merge_short_segments(subs, min_duration=3.0):
    """
    合并短于指定时长的字幕片段到下一句
    :param subs: pysrt字幕对象列表
    :param min_duration: 最小持续时间（秒）
    :return: 合并后的字幕字典列表
    """
    merged_segments = []
    i = 0
    while i < len(subs):
        start_seconds = (
                subs[i].start.hours * 3600 +
                subs[i].start.minutes * 60 +
                subs[i].start.seconds +
                subs[i].start.milliseconds / 1000.0
        )
        end_seconds = (
                subs[i].end.hours * 3600 +
                subs[i].end.minutes * 60 +
                subs[i].end.seconds +
                subs[i].end.milliseconds / 1000.0
        )
        duration = end_seconds - start_seconds

        if duration < min_duration and i < len(subs) - 1:
            merged_text = subs[i].text
            merged_end = subs[i].end
            j = i + 1

            while j < len(subs):
                new_end_seconds = (
                        subs[j].end.hours * 3600 +
                        subs[j].end.minutes * 60 +
                        subs[j].end.seconds +
                        subs[j].end.milliseconds / 1000.0
                )
                merged_duration = new_end_seconds - start_seconds

                merged_text = f"{merged_text} {subs[j].text}".strip()

                merged_end = subs[j].end

                if merged_duration >= min_duration:
                    j += 1
                    break

                j += 1

            merged_segments.append({
                'start': subs[i].start,
                'end': merged_end,
                'text': merged_text,
                'original_indexes': list(range(i, j))
            })
            i = j
        else:
            merged_segments.append({
                'start': subs[i].start,
                'end': subs[i].end,
                'text': subs[i].text,
                'original_indexes': [i]
            })
            i += 1

    return merged_segments


def cut_audio_by_srt(video_path, srt_path, output_dir):
    """
    根据SRT字幕文件切割视频生成音频片段和文本文件
    :param video_path: 输入视频文件路径
    :param srt_path: SRT字幕文件路径
    :param output_dir: 输出目录路径
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        subs = pysrt.open(srt_path)
    except Exception as e:
        print(f"错误: 无法解析字幕文件 {srt_path} - {str(e)}")
        return

    merged_segments = merge_short_segments(subs)
    print(f"原始字幕数: {len(subs)}, 合并后片段数: {len(merged_segments)}")

    # 记录音频和文本的对应关系
    audio_text_dict = dict()
    for i, segment in enumerate(merged_segments, 1):
        start_seconds = (
                segment['start'].hours * 3600 +
                segment['start'].minutes * 60 +
                segment['start'].seconds +
                segment['start'].milliseconds / 1000.0
        )
        end_seconds = (
                segment['end'].hours * 3600 +
                segment['end'].minutes * 60 +
                segment['end'].seconds +
                segment['end'].milliseconds / 1000.0
        )

        duration = end_seconds - start_seconds
        if duration <= 0.1:
            print(f"警告: 跳过无效时间段 {start_seconds} - {end_seconds} (片段 #{i})")
            continue

        output_wav = os.path.join(output_dir, f"segment_{i:03d}.wav")
        output_txt = os.path.join(output_dir, f"segment_{i:03d}.txt")
        all_csv = os.path.join(output_dir, "segment_all.csv")

        audio_text_dict[output_wav] = segment['text']

        try:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(segment['text'])
        except Exception as e:
            print(f"文本文件写入错误: {str(e)}")

        try:
            (
                ffmpeg
                .input(video_path, ss=start_seconds)
                .output(output_wav, t=duration, acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            start_str = f"{segment['start'].hours:02d}:{segment['start'].minutes:02d}:{segment['start'].seconds:02d}.{segment['start'].milliseconds:03d}"
            end_str = f"{segment['end'].hours:02d}:{segment['end'].minutes:02d}:{segment['end'].seconds:02d}.{segment['end'].milliseconds:03d}"
            print(f"已生成音频: {output_wav}")
            print(f"  时长: {duration:.2f}秒 | {start_str} - {end_str}")
            print(f"  文本: {segment['text'][:50]}... ({len(segment['text'])}字符)")
            print(f"  合并了 {len(segment['original_indexes'])} 个原始片段")
        except ffmpeg.Error as e:
            print(f"FFmpeg处理错误: {str(e)}")
        except Exception as e:
            print(f"未知错误: {str(e)}")
        print("-" * 80)
        # 写入一个总的文件记录音频和对应的文本的关系
        with open(all_csv, 'w', encoding='utf-8') as f:
            for audio_path, audio_content in audio_text_dict.items():
                f.writelines(audio_path + ' ' + audio_content.replace(' ', '') + '\n')


def process_directory(input_dir, output_base_dir, video_exts=('*.mp4',)):
    """
    处理目录中的所有视频文件
    :param input_dir: 输入目录路径
    :param output_base_dir: 输出基础目录路径
    :param video_exts: 视频文件扩展名列表
    """
    video_files = []
    for ext in video_exts:
        video_files.extend(glob.glob(os.path.join(input_dir, ext)))

    print(f"找到 {len(video_files)} 个视频文件")

    for video_path in video_files:
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        srt_candidates = [os.path.join(input_dir, f"{base_name}.srt"),]

        srt_path = None
        for candidate in srt_candidates:
            if os.path.exists(candidate):
                srt_path = candidate
                break

        if srt_path:
            print(f"处理视频: {video_path} 使用字幕: {srt_path}")
            video_output_dir = os.path.join(output_base_dir, base_name)
            cut_audio_by_srt(video_path, srt_path, video_output_dir)
        else:
            print(f"警告: 找不到 {base_name} 的字幕文件，跳过")


if __name__ == "__main__":
    INPUT_DIR = r"D:\Works\ASR\客家话\data\自己收集的数据集\youtube"
    OUTPUT_DIR = "youtube"
    process_directory(INPUT_DIR, OUTPUT_DIR)
