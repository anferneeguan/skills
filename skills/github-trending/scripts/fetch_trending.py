#!/usr/bin/env python3
"""
Fetch top trending repositories from GitHub.

This script scrapes the actual GitHub trending page to get the real trending repos,
since GitHub doesn't provide an official API for trending.
"""

import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def fetch_trending_repos(count=5, since='daily'):
    """
    Fetch trending repositories from GitHub by scraping the trending page.

    Args:
        count: Number of repositories to fetch (default: 5)
        since: Time range - 'daily', 'weekly', or 'monthly' (default: 'daily')

    Returns:
        List of repository dictionaries with relevant information
    """
    url = f'https://github.com/trending?since={since}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=15) as response:
            html = response.read().decode('utf-8')

        repos = []

        # Parse the HTML to extract repository information
        # GitHub trending page structure: each repo is in an article tag with class "Box-row"
        repo_pattern = r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>'
        repo_blocks = re.findall(repo_pattern, html, re.DOTALL)

        for block in repo_blocks[:count]:
            try:
                # Extract repository name (owner/repo)
                name_match = re.search(r'<h2[^>]*>.*?<a[^>]*href="/([^"]+)"', block, re.DOTALL)
                if not name_match:
                    continue
                name = name_match.group(1).strip()

                # Extract description
                desc_match = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL)
                description = 'No description provided'
                if desc_match:
                    description = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
                    description = re.sub(r'\s+', ' ', description)

                # Extract language
                lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', block)
                language = lang_match.group(1).strip() if lang_match else 'Not specified'

                # Extract stars (total)
                stars_match = re.search(r'<svg[^>]*octicon-star[^>]*>.*?</svg>\s*<span[^>]*>([\d,]+)</span>', block, re.DOTALL)
                stars = 0
                if stars_match:
                    stars = int(stars_match.group(1).replace(',', ''))

                # Extract stars today
                stars_today_match = re.search(r'<span[^>]*class="[^"]*float-sm-right[^"]*"[^>]*>.*?([\d,]+)\s+stars?\s+today', block, re.DOTALL)
                stars_today = 0
                if stars_today_match:
                    stars_today = int(stars_today_match.group(1).replace(',', ''))

                repo = {
                    'name': name,
                    'description': description,
                    'language': language,
                    'stars': stars,
                    'stars_today': stars_today,
                    'url': f'https://github.com/{name}'
                }
                repos.append(repo)

            except Exception as e:
                # Skip this repo if parsing fails
                continue

        return repos

    except HTTPError as e:
        print(json.dumps({
            'error': f'HTTP Error {e.code}',
            'details': str(e)
        }), file=sys.stderr)
        sys.exit(1)

    except URLError as e:
        print(json.dumps({
            'error': 'Network error',
            'details': str(e)
        }), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(json.dumps({
            'error': 'Unexpected error',
            'details': str(e)
        }), file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    # Get count from command line or use default
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    # Get time range from command line or use default
    since = sys.argv[2] if len(sys.argv) > 2 else 'daily'

    if since not in ['daily', 'weekly', 'monthly']:
        print(json.dumps({
            'error': 'Invalid time range',
            'details': 'since must be one of: daily, weekly, monthly'
        }), file=sys.stderr)
        sys.exit(1)

    repos = fetch_trending_repos(count=count, since=since)

    if not repos:
        print(json.dumps({
            'error': 'No repositories found',
            'details': 'Could not parse trending repositories from GitHub'
        }), file=sys.stderr)
        sys.exit(1)

    # Output as JSON for easy parsing
    print(json.dumps(repos, indent=2))


if __name__ == '__main__':
    main()
