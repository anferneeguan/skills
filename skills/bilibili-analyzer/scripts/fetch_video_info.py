#!/usr/bin/env python3
"""
Fetch Bilibili video information including metadata, subtitles, and comments.
"""

import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs


def extract_bvid(url):
    """Extract BV ID from Bilibili URL."""
    # Support formats:
    # https://www.bilibili.com/video/BV1xx411c7mD
    # https://b23.tv/xxxxx (short link)

    if 'BV' in url:
        match = re.search(r'(BV[a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)

    # Handle short links by following redirect
    if 'b23.tv' in url:
        try:
            request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(request) as response:
                final_url = response.geturl()
                return extract_bvid(final_url)
        except:
            pass

    return None


def fetch_video_info(bvid):
    """
    Fetch video information from Bilibili API.

    Args:
        bvid: Bilibili video ID (e.g., BV1xx411c7mD)

    Returns:
        Dictionary with video information
    """
    # Bilibili API endpoint
    api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }

    try:
        request = Request(api_url, headers=headers)
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data['code'] != 0:
            return {
                'error': 'Failed to fetch video info',
                'details': data.get('message', 'Unknown error')
            }

        video_data = data['data']

        # Extract key information
        info = {
            'bvid': bvid,
            'title': video_data['title'],
            'description': video_data['desc'],
            'duration': video_data['duration'],  # in seconds
            'duration_formatted': format_duration(video_data['duration']),
            'cover': video_data['pic'],
            'pubdate': video_data['pubdate'],
            'owner': {
                'name': video_data['owner']['name'],
                'mid': video_data['owner']['mid']
            },
            'stats': {
                'views': video_data['stat']['view'],
                'likes': video_data['stat']['like'],
                'coins': video_data['stat']['coin'],
                'favorites': video_data['stat']['favorite'],
                'shares': video_data['stat']['share'],
                'danmaku': video_data['stat']['danmaku'],
                'replies': video_data['stat']['reply']
            },
            'tags': [tag['tag_name'] for tag in video_data.get('tag', [])],
            'cid': video_data['cid'],  # needed for subtitle fetching
            'url': f'https://www.bilibili.com/video/{bvid}'
        }

        return info

    except HTTPError as e:
        return {
            'error': f'HTTP Error {e.code}',
            'details': str(e)
        }
    except URLError as e:
        return {
            'error': 'Network error',
            'details': str(e)
        }
    except Exception as e:
        return {
            'error': 'Unexpected error',
            'details': str(e)
        }


def fetch_subtitles(bvid, cid):
    """
    Fetch video subtitles if available.

    Args:
        bvid: Bilibili video ID
        cid: Video CID (from video info)

    Returns:
        List of subtitle entries or None
    """
    # Subtitle API endpoint
    api_url = f'https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }

    try:
        request = Request(api_url, headers=headers)
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data['code'] != 0:
            return None

        subtitle_info = data['data'].get('subtitle')
        if not subtitle_info or not subtitle_info.get('subtitles'):
            return None

        # Get the first available subtitle (usually Chinese)
        subtitle_url = 'https:' + subtitle_info['subtitles'][0]['subtitle_url']

        request = Request(subtitle_url, headers=headers)
        with urlopen(request, timeout=10) as response:
            subtitle_data = json.loads(response.read().decode('utf-8'))

        # Format subtitles
        subtitles = []
        for item in subtitle_data.get('body', []):
            subtitles.append({
                'from': item['from'],
                'to': item['to'],
                'text': item['content']
            })

        return subtitles

    except:
        return None


def fetch_top_comments(bvid, count=10):
    """
    Fetch top comments for the video.

    Args:
        bvid: Bilibili video ID
        count: Number of comments to fetch

    Returns:
        List of top comments
    """
    # Get aid (av number) first
    api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }

    try:
        request = Request(api_url, headers=headers)
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data['code'] != 0:
            return []

        aid = data['data']['aid']

        # Fetch comments
        comment_url = f'https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=2&ps={count}'

        request = Request(comment_url, headers=headers)
        with urlopen(request, timeout=10) as response:
            comment_data = json.loads(response.read().decode('utf-8'))

        if comment_data['code'] != 0:
            return []

        comments = []
        for reply in comment_data['data'].get('replies', [])[:count]:
            comments.append({
                'user': reply['member']['uname'],
                'content': reply['content']['message'],
                'likes': reply['like']
            })

        return comments

    except:
        return []


def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    else:
        return f'{minutes:02d}:{secs:02d}'


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Missing video URL',
            'usage': 'python fetch_video_info.py <bilibili_url>'
        }), file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    # Extract BV ID
    bvid = extract_bvid(url)
    if not bvid:
        print(json.dumps({
            'error': 'Invalid Bilibili URL',
            'details': 'Could not extract BV ID from URL'
        }), file=sys.stderr)
        sys.exit(1)

    # Fetch video info
    info = fetch_video_info(bvid)

    if 'error' in info:
        print(json.dumps(info, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    # Fetch subtitles
    subtitles = fetch_subtitles(bvid, info['cid'])
    if subtitles:
        info['subtitles'] = subtitles

    # Fetch top comments
    comments = fetch_top_comments(bvid, count=10)
    if comments:
        info['top_comments'] = comments

    # Output as JSON
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
