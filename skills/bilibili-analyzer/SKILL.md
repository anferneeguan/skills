---
name: bilibili-analyzer
description: Analyzes Bilibili video content including visual frames, subtitles, metadata, comments, and danmaku. Use this skill when users want to understand what a Bilibili video is about, get a summary, or analyze video content without watching the full video. Supports both text-based analysis (metadata, subtitles, comments) and visual analysis (video frames).
---

# Bilibili Video Analyzer

This skill provides comprehensive analysis of Bilibili videos by combining visual frame analysis, text content (subtitles, comments, danmaku), and metadata.

## Workflow

1. **Extract video information**
   - Run `scripts/fetch_video_info.py <video_url>` to get metadata, subtitles, and comments
   - Returns: title, description, tags, views, likes, UP主 info, subtitles (if available)

2. **Download and extract frames**
   - Run `scripts/download_video.py <video_url> <output_dir>` to download video
   - Run `scripts/extract_frames.py <video_path> <output_dir> [interval]` to extract key frames
   - Interval options:
     - `auto`: Smart scene change detection (recommended)
     - `10`: Extract one frame every 10 seconds
     - `30`: Extract one frame every 30 seconds

3. **Analyze visual content**
   - Use Claude's vision capabilities to analyze each extracted frame
   - Identify: text, code, charts, diagrams, people, scenes, UI elements
   - Understand the visual narrative and key information

4. **Generate comprehensive report**
   - Combine metadata, subtitles, comments, danmaku, and visual analysis
   - Provide structured summary with key points, topics, and insights

## Output Format

```markdown
# Bilibili 视频分析报告

## 基本信息
- 标题: [video title]
- UP主: [uploader name]
- 时长: [duration]
- 播放量: [views] | 点赞: [likes] | 投币: [coins]
- 发布时间: [publish date]

## 内容摘要
[综合字幕、画面、评论的整体内容概述]

## 视觉内容分析
### 关键画面
1. [时间戳] - [画面描述和关键信息]
2. [时间戳] - [画面描述和关键信息]
...

## 核心要点
1. [要点1]
2. [要点2]
...

## 观众反馈
- 热门弹幕: [top danmaku]
- 高赞评论: [top comments]

## 推荐指数
⭐⭐⭐⭐⭐ [评分理由]
```

## Guidelines

- **Smart frame extraction**: For videos longer than 10 minutes, use scene change detection to avoid redundant frames
- **Frame analysis**: Focus on extracting text, identifying key visual elements, and understanding context
- **Combine sources**: Synthesize information from all sources (visual, text, metadata) for comprehensive understanding
- **Respect content**: Provide objective analysis without bias
- **Handle errors gracefully**: If subtitles or frames are unavailable, work with available data

## Dependencies

The scripts require the following tools:
- `yt-dlp` or `you-get`: For downloading Bilibili videos
- `ffmpeg`: For extracting video frames
- Python packages: `requests`, `beautifulsoup4`, `Pillow`

Install with:
```bash
pip install yt-dlp requests beautifulsoup4 Pillow
brew install ffmpeg  # macOS
```

## Example Usage

User: "帮我分析这个B站视频 https://www.bilibili.com/video/BV1xx411c7mD"
User: "这个视频讲了什么？https://www.bilibili.com/video/BV1234567890"
User: "Analyze this Bilibili video for me: [URL]"

## Notes

- Video download may take time depending on video length and quality
- Frame extraction is optimized to balance detail and efficiency
- Visual analysis works best with clear, high-quality frames
- Some videos may have region restrictions or require login
