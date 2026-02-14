#!/usr/bin/env python3
"""
Download Bilibili video using yt-dlp.
"""

import json
import subprocess
import sys
import os


def download_video(url, output_dir='.', quality='best'):
    """
    Download Bilibili video.

    Args:
        url: Bilibili video URL
        output_dir: Directory to save the video
        quality: Video quality ('best', 'worst', or specific format)

    Returns:
        Path to downloaded video file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Output template
    output_template = os.path.join(output_dir, '%(id)s.%(ext)s')

    # yt-dlp command
    cmd = [
        'yt-dlp',
        '--format', quality,
        '--output', output_template,
        '--no-playlist',
        '--print', 'after_move:filepath',  # Print final file path
        url
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Get the file path from output
        filepath = result.stdout.strip().split('\n')[-1]

        return {
            'success': True,
            'filepath': filepath,
            'output_dir': output_dir
        }

    except subprocess.CalledProcessError as e:
        return {
            'error': 'Download failed',
            'details': e.stderr
        }
    except FileNotFoundError:
        return {
            'error': 'yt-dlp not found',
            'details': 'Please install yt-dlp: pip install yt-dlp'
        }
    except Exception as e:
        return {
            'error': 'Unexpected error',
            'details': str(e)
        }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Missing video URL',
            'usage': 'python download_video.py <bilibili_url> [output_dir] [quality]'
        }), file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './videos'
    quality = sys.argv[3] if len(sys.argv) > 3 else 'best'

    print(f'Downloading video from {url}...', file=sys.stderr)

    result = download_video(url, output_dir, quality)

    if 'error' in result:
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
