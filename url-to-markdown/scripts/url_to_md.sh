#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <url> [output.md]\n' "$(basename "$0")"
  printf 'Example: %s https://www.arthropod.software/p/vibe-coding-our-way-to-disaster\n' "$(basename "$0")"
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 1
fi

url="$1"
output="${2:-}"

if [[ -z "$output" ]]; then
  clean_url="${url%%\#*}"
  clean_url="${clean_url%%\?*}"
  filename="${clean_url##*/}"

  if [[ -z "$filename" ]]; then
    filename="output"
  fi

  base_name="${filename%.*}"
  if [[ -z "$base_name" || "$base_name" == "$filename" ]]; then
    base_name="$filename"
  fi

  output="${base_name}.md"
fi

if command -v uv >/dev/null 2>&1; then
  py_runner=(uv run --quiet --with requests --with trafilatura --with markdownify python3)
else
  if ! command -v python3 >/dev/null 2>&1; then
    printf 'Error: python3 is not installed.\n' >&2
    exit 1
  fi
  py_runner=(python3)
fi

"${py_runner[@]}" - "$url" "$output" <<'PY'
import re
import sys

try:
    import requests
except ImportError:
    print('Error: missing Python package "requests". Install with: pip install requests trafilatura markdownify', file=sys.stderr)
    sys.exit(1)

try:
    import trafilatura
except ImportError:
    print('Error: missing Python package "trafilatura". Install with: pip install trafilatura markdownify requests', file=sys.stderr)
    sys.exit(1)

try:
    from markdownify import markdownify
except ImportError:
    print('Error: missing Python package "markdownify". Install with: pip install markdownify trafilatura requests', file=sys.stderr)
    sys.exit(1)


NOISE_PATTERNS = [
    r"^subscribe\b",
    r"^share\b",
    r"^like\b",
    r"^comment\b",
    r"^thanks for reading\b",
    r"^download the app\b",
    r"^start writing\b",
    r"^discover more from\b",
]


def clean_lines(text: str) -> str:
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue

        lowered = stripped.lower()
        if any(re.match(p, lowered) for p in NOISE_PATTERNS):
            continue
        out.append(line.rstrip())

    cleaned = "\n".join(out)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned + "\n"


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_markdown(html: str) -> str:
    extracted_html = trafilatura.extract(
        html,
        output_format="html",
        include_links=False,
        include_images=False,
        include_tables=False,
        include_comments=False,
        favor_precision=True,
        deduplicate=True,
    )

    if extracted_html:
        return clean_lines(markdownify(extracted_html, heading_style="ATX"))

    extracted_text = trafilatura.extract(
        html,
        output_format="txt",
        include_comments=False,
        favor_precision=True,
        deduplicate=True,
    )

    if extracted_text:
        return clean_lines(extracted_text)

    raise RuntimeError("Could not extract article content from URL")


def main() -> int:
    url = sys.argv[1]
    output = sys.argv[2]

    html = fetch_html(url)
    content = extract_markdown(html)

    with open(output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
