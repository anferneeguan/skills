#!/usr/bin/env python3
"""
Analyze video frames using Claude's vision API.
"""

import json
import sys
import os
import base64
from pathlib import Path


def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def analyze_frames(frames_dir, sample_count=8):
    """
    Analyze video frames.

    Args:
        frames_dir: Directory containing frame images
        sample_count: Number of frames to analyze (default: 8)

    Returns:
        Analysis results
    """
    frames_path = Path(frames_dir)

    if not frames_path.exists():
        return {
            'error': 'Frames directory not found',
            'details': f'Directory {frames_dir} does not exist'
        }

    # Get all frame files
    frame_files = sorted(frames_path.glob('frame_*.jpg'))

    if not frame_files:
        return {
            'error': 'No frames found',
            'details': f'No frame_*.jpg files in {frames_dir}'
        }

    # Sample frames evenly
    total_frames = len(frame_files)
    if total_frames <= sample_count:
        selected_frames = frame_files
    else:
        step = total_frames // sample_count
        selected_frames = [frame_files[i * step] for i in range(sample_count)]

    # Prepare frame data
    frames_data = []
    for frame_path in selected_frames:
        try:
            # Get frame info
            frame_info = {
                'path': str(frame_path),
                'name': frame_path.name,
                'size': frame_path.stat().st_size,
                'base64': encode_image(frame_path)
            }
            frames_data.append(frame_info)
        except Exception as e:
            print(f"Warning: Failed to process {frame_path}: {e}", file=sys.stderr)
            continue

    if not frames_data:
        return {
            'error': 'Failed to process frames',
            'details': 'Could not read any frame files'
        }

    # Return frame data for analysis
    # Note: Actual Claude API call would happen here
    # For now, we return the frame data structure
    result = {
        'success': True,
        'total_frames': total_frames,
        'analyzed_frames': len(frames_data),
        'frames': [
            {
                'name': f['name'],
                'path': f['path'],
                'size': f['size'],
                'base64_length': len(f['base64'])
            }
            for f in frames_data
        ],
        'note': 'Frame data prepared. To complete analysis, these frames need to be sent to Claude API with vision capabilities.'
    }

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Missing frames directory',
            'usage': 'python analyze_frames.py <frames_dir> [sample_count]'
        }), file=sys.stderr)
        sys.exit(1)

    frames_dir = sys.argv[1]
    sample_count = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    result = analyze_frames(frames_dir, sample_count)

    if 'error' in result:
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
