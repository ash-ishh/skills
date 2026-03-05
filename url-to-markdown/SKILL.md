---
name: url-to-markdown
description: Convert web pages to clean markdown files. Use this skill whenever users want to fetch web content, extract articles, save web pages locally, or need URLs converted to markdown for context. Works with articles, blog posts, documentation. Automatically removes ads, navigation, and social media clutter. Triggers on phrases like "get this article", "save this webpage", "convert this URL to markdown", or when users provide URLs that need to be processed.
---

# URL to Markdown Converter

Fetches web pages and converts them to clean markdown files, removing ads and web clutter.

## Usage

```bash
# Auto-generate filename from URL
scripts/url_to_md.sh <url>

# Specify output filename
scripts/url_to_md.sh <url> <output.md>
```

## Examples

```bash
# Fetch an article
scripts/url_to_md.sh https://example.com/article-about-ai
# Creates: article-about-ai.md

# Save with custom name
scripts/url_to_md.sh https://docs.python.org/3/tutorial/index.html python-tutorial.md

# Research collection
scripts/url_to_md.sh https://arxiv.org/abs/2301.00234 paper1.md
scripts/url_to_md.sh https://openai.com/research/gpt-4 gpt4-research.md
```

## Features

- Extracts main content using `trafilatura`
- Converts to clean markdown with `markdownify`
- Removes ads, navigation, social media buttons
- Auto-filters noise like "subscribe", "share", "comment" prompts
- Handles UTF-8 encoding properly

## Requirements

Automatically handled by the script:
- Python 3
- requests, trafilatura, markdownify (installed via pip or uv)

## Limitations

- Needs internet connection
- Can't handle authenticated pages
- JavaScript-heavy sites may not extract well
- Paywalled content shows only preview