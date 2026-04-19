# URL to Markdown

Convert a web page into a clean local Markdown file with `scripts/url_to_md.sh`.

## What this skill does

- Fetches a URL
- Extracts the main article content
- Removes common web clutter
- Saves the result as Markdown

## Usage

```bash
# Auto-generate filename from URL
scripts/url_to_md.sh <url>

# Specify output filename
scripts/url_to_md.sh <url> <output.md>
```

## Examples

```bash
scripts/url_to_md.sh https://example.com/article-about-ai
scripts/url_to_md.sh https://docs.python.org/3/tutorial/index.html python-tutorial.md
scripts/url_to_md.sh https://arxiv.org/abs/2301.00234 paper1.md
```

## How it works

The script prefers `uv` if available. Otherwise it falls back to `python3`.

It uses:

- `requests` for fetching
- `trafilatura` for main-content extraction
- `markdownify` for Markdown conversion

## Requirements

- Internet access
- `uv` or `python3`

If `uv` is installed, dependencies are handled automatically at runtime.

## Limitations

- Authenticated pages are not supported
- JavaScript-heavy pages may extract poorly
- Paywalled pages usually return only visible preview text

## Output

If you do not pass an output filename, the script derives one from the URL path.

Example:

```bash
scripts/url_to_md.sh https://example.com/posts/my-article
```

Creates:

```text
my-article.md
```
