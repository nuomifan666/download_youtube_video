import os
import uuid
from pytubefix import YouTube
from moviepy.editor import AudioFileClip
#批量下载视频并实现视频裁剪，转换为wav格式。

def download_youtube_as_wav(url, output_dir, filename=None, start_time=None, end_time=None):
    os.makedirs(output_dir, exist_ok=True)

    try:
        yt = YouTube(url)
        title = yt.title.replace(" ", "_").replace("/", "_").replace("|", "_")  # 清理非法字符
        if filename is None:
            # 用 UUID 确保唯一文件名
            filename = f"{title}_{uuid.uuid4().hex[:8]}.wav"

        print(f"正在下载: {yt.title}")
        stream = yt.streams.filter(only_audio=True).first()
        temp_file = stream.download(output_path=output_dir, filename="temp.mp4")

        # 加载音频
        audio = AudioFileClip(temp_file)

        # 如果指定了开始和结束时间，截取片段
        if start_time and end_time:
            audio = audio.subclip(start_time, end_time)

        # 输出路径
        wav_path = os.path.join(output_dir, filename)
        audio.write_audiofile(wav_path, codec='pcm_s16le')
        audio.close()

        os.remove(temp_file)
        print(f"完成: {wav_path}\n")
        return wav_path

    except Exception as e:
        print(f"下载失败: {url}\n错误信息: {e}")
        return None


def parse_time(timestr):
    """把 00:01:10 转换为秒数 (70)"""
    parts = list(map(int, timestr.split(":")))
    if len(parts) == 3:
        h, m, s = parts
        return h*3600 + m*60 + s
    elif len(parts) == 2:
        m, s = parts
        return m*60 + s
    else:
        return int(parts[0])


if __name__ == "__main__":
    urls_file = "urls.txt"
    output_dir = r"D:\doucumt\配音\9.15"

    if not os.path.exists(urls_file):
        print(f"未找到 {urls_file} 文件，请先创建并在里面写入YouTube链接。")
    else:
        with open(urls_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        seen = {}
        for i, line in enumerate(urls, start=1):
            parts = line.split()
            url = parts[0]
            start_time = parse_time(parts[1]) if len(parts) > 1 else None
            end_time = parse_time(parts[2]) if len(parts) > 2 else None

            if url in seen:
                print(f"⚠️ 跳过: 第 {i} 行 的网址与第 {seen[url]} 行重复 -> {url}")
                continue
            else:
                seen[url] = i

            # 不再用序号命名，直接交给函数生成随机名
            download_youtube_as_wav(url, output_dir, None, start_time, end_time)
