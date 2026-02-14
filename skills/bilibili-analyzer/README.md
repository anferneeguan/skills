# Bilibili Video Analyzer - 使用说明

这个技能可以全面分析 Bilibili 视频内容，包括视觉画面、字幕、评论和弹幕。

## 快速开始

### 1. 安装依赖

```bash
# 安装 Python 包
pip install yt-dlp requests beautifulsoup4 Pillow

# 安装 ffmpeg (macOS)
brew install ffmpeg

# 安装 ffmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# 安装 ffmpeg (Windows)
# 从 https://ffmpeg.org/download.html 下载
```

### 2. 使用示例

```bash
# 步骤 1: 获取视频信息（元数据、字幕、评论）
python scripts/fetch_video_info.py "https://www.bilibili.com/video/BV1xx411c7mD"

# 步骤 2: 下载视频
python scripts/download_video.py "https://www.bilibili.com/video/BV1xx411c7mD" ./videos

# 步骤 3: 提取关键帧
python scripts/extract_frames.py ./videos/BV1xx411c7mD.mp4 ./frames auto

# 步骤 4: 让 Claude 分析提取的帧和信息
```

## 脚本说明

### fetch_video_info.py
获取视频的元数据、字幕（如果有）和热门评论。

**输出示例**:
```json
{
  "title": "视频标题",
  "description": "视频简介",
  "duration": 932,
  "duration_formatted": "15:32",
  "owner": {"name": "UP主名称"},
  "stats": {
    "views": 105000,
    "likes": 8234,
    "coins": 1234
  },
  "subtitles": [...],
  "top_comments": [...]
}
```

### download_video.py
使用 yt-dlp 下载视频。

**参数**:
- `url`: 视频链接
- `output_dir`: 保存目录（默认: ./videos）
- `quality`: 视频质量（默认: best）

### extract_frames.py
从视频中提取关键帧。

**参数**:
- `video_path`: 视频文件路径
- `output_dir`: 帧保存目录
- `interval`: 提取间隔
  - `auto`: 智能场景检测（推荐）
  - `10`: 每 10 秒一帧
  - `30`: 每 30 秒一帧

**智能提取**:
- 短视频（<5分钟）: 每 10 秒
- 中等视频（5-30分钟）: 场景检测
- 长视频（>30分钟）: 每 30 秒或场景检测

## 分析流程

1. **文本信息**: 标题、简介、标签、评论、弹幕
2. **视觉内容**: 关键帧中的文字、图表、代码、场景
3. **综合理解**: 结合所有信息生成完整分析报告

## 注意事项

- 某些视频可能有地区限制
- 下载时间取决于视频长度和网络速度
- 建议使用 `auto` 模式提取帧，自动优化数量
- 提取的帧会保存为 JPG 格式，便于 Claude 分析
