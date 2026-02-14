---
name: github-trending
description: Collects and summarizes the top 5 daily trending repositories from GitHub. Use this skill when users ask about GitHub trending projects, popular repositories today, what's trending on GitHub, or want to discover new popular projects.
---

# GitHub Trending Collector

This skill helps collect and present the top 5 daily trending repositories from GitHub with concise summaries.

## Workflow

1. **Execute the fetch script**: Run `scripts/fetch_trending.py` to scrape the actual GitHub trending page
   - The script accepts optional parameters: count and time range
   - Usage: `python scripts/fetch_trending.py [count] [since]`
   - Count: number of repos to fetch (default: 5)
   - Since: 'daily', 'weekly', or 'monthly' (default: 'daily')
   - Example: `python scripts/fetch_trending.py 5 daily`

2. **Parse the JSON output**: The script returns structured JSON with:
   - Repository name (owner/repo)
   - Description
   - Primary language
   - Total stars count
   - Stars gained today/this week/this month
   - Repository URL

3. **Present results**: Format the data as a numbered list with clear, concise summaries

## Output Format

Present results in this structure:

```
# GitHub Trending Repositories

1. **[owner/repo-name](link)**
   - Description: [project description]
   - Language: [primary language]
   - Stars: [total stars] (+[stars today/week/month] today/this week/this month)
   - Summary: [1-2 sentence explanation of what makes it interesting]

2. [repeat for each project]
```

## Guidelines

- The script scrapes the actual GitHub trending page (https://github.com/trending)
- This matches exactly what you see on the official trending page
- Keep summaries concise (1-2 sentences per project)
- Include the direct GitHub link for each project
- Highlight the stars gained in the time period (today/week/month)
- If fewer than requested projects are available, show what's available
- Default time range is 'daily' - use 'weekly' or 'monthly' for different views

## Example Usage

User: "What's trending on GitHub today?"
User: "Show me the top 5 GitHub trending projects"
User: "帮我看看 GitHub 今天有什么热门项目"
