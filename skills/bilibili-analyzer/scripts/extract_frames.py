#!/usr/bin/env python3
"""
Extract key frames from video using ffmpeg.
"""

import json
import subprocess
import sys
import os
from pathlib import Path


def get_ffmpeg_path():
    """Get ffmpeg path, checking common locations."""
    paths = [
        'ffmpeg',  # In PATH
        os.path.expanduser('~/bin/ffmpeg'),  # User bin
        '/usr/local/bin/ffmpeg',  # Homebrew Intel
        '/opt/homebrew/bin/ffmpeg',  # Homebrew Apple Silicon
    ]
    for path in paths:
        try:
            subprocess.run([path, '-version'], capture_output=True, check=True)
            return path
        except:
            continue
    return 'ffmpeg'  # Fallback


def extract_frames_interval(video_path, output_dir, interval=10):
    """
    Extract frames at regular intervals.

    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        interval: Seconds between frames

    Returns:
        List of extracted frame paths
    """
    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    ffmpeg = get_ffmpeg_path()
    cmd = [
        ffmpeg,
        '-i', video_path,
        '-vf', f'fps=1/{interval}',
        '-q:v', '2',  # High quality
        output_pattern,
        '-y'  # Overwrite existing files
    ]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Get list of extracted frames
        frames = sorted(Path(output_dir).glob('frame_*.jpg'))
        frame_paths = [str(f) for f in frames]

        return {
            'success': True,
            'method': 'interval',
            'interval': interval,
            'frame_count': len(frame_paths),
            'frames': frame_paths
        }

    except subprocess.CalledProcessError as e:
        return {
            'error': 'Frame extraction failed',
            'details': e.stderr
        }
    except FileNotFoundError:
        return {
            'error': 'ffmpeg not found',
            'details': 'Please install ffmpeg'
        }
    except Exception as e:
        return {
            'error': 'Unexpected error',
            'details': str(e)
        }


def extract_frames_scene(video_path, output_dir, threshold=0.3):
    """
    Extract frames at scene changes (smart detection).

    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        threshold: Scene change detection threshold (0.0-1.0)

    Returns:
        List of extracted frame paths
    """
    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, 'scene_%04d.jpg')

    ffmpeg = get_ffmpeg_path()
    cmd = [
        ffmpeg,
        '-i', video_path,
        '-vf', f'select=gt(scene\\,{threshold})',
        '-vsync', 'vfr',
        '-q:v', '2',
        output_pattern,
        '-y'
    ]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Get list of extracted frames
        frames = sorted(Path(output_dir).glob('scene_*.jpg'))
        frame_paths = [str(f) for f in frames]

        return {
            'success': True,
            'method': 'scene_detection',
            'threshold': threshold,
            'frame_count': len(frame_paths),
            'frames': frame_paths
        }

    except subprocess.CalledProcessError as e:
        return {
            'error': 'Frame extraction failed',
            'details': e.stderr
        }
    except FileNotFoundError:
        return {
            'error': 'ffmpeg not found',
            'details': 'Please install ffmpeg'
        }
    except Exception as e:
        return {
            'error': 'Unexpected error',
            'details': str(e)
        }


def get_video_duration(video_path):
    """Get video duration in seconds."""
    ffprobe = get_ffmpeg_path().replace('ffmpeg', 'ffprobe')
    cmd = [
        ffprobe,
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(json.dumps({
            'error': 'Missing arguments',
            'usage': 'python extract_frames.py <video_path> <output_dir> [interval|auto]'
        }), file=sys.stderr)
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else 'auto'

    if not os.path.exists(video_path):
        print(json.dumps({
            'error': 'Video file not found',
            'path': video_path
        }), file=sys.stderr)
        sys.exit(1)

    print(f'Extracting frames from {video_path}...', file=sys.stderr)

    # Determine extraction method
    if mode == 'auto':
        # Use scene detection for smart extraction
        result = extract_frames_scene(video_path, output_dir)

        # If too many or too few frames, fall back to interval
        if result.get('frame_count', 0) > 50 or result.get('frame_count', 0) < 5:
            duration = get_video_duration(video_path)
            if duration:
                # Calculate appropriate interval
                interval = max(10, int(duration / 30))  # Target ~30 frames
                result = extract_frames_interval(video_path, output_dir, interval)
    else:
        # Use specified interval
        try:
            interval = int(mode)
            result = extract_frames_interval(video_path, output_dir, interval)
        except ValueError:
            print(json.dumps({
                'error': 'Invalid interval',
                'details': 'Interval must be a number or "auto"'
            }), file=sys.stderr)
            sys.exit(1)

    if 'error' in result:
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
