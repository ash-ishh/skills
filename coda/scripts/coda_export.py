#!/usr/bin/env python3
"""Export Coda page trees to Markdown files.

Usage examples:
  python coda_export.py list-pages --doc-id <DOC_ID> --token <TOKEN>
  python coda_export.py export-subtree --doc-id <DOC_ID> --token <TOKEN> --root-page-id canvas-abc123

Environment fallback:
  CENTRAL_BRAIN_DOC_ID
  CODA_CENTRAL_BRAIN_TOKEN
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://coda.io/apis/v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Coda page exporter")
    parser.add_argument(
        "--doc-id",
        default=None,
        help="Coda doc ID (or set CENTRAL_BRAIN_DOC_ID)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Coda API token (or set CODA_CENTRAL_BRAIN_TOKEN)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="HTTP timeout in seconds (default: 90)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=6,
        help="Number of retry attempts for transient failures (default: 6)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list-pages", help="List all pages in a Coda doc"
    )
    list_parser.add_argument(
        "--contains",
        default=None,
        help="Optional case-insensitive filter by page name",
    )

    export_parser = subparsers.add_parser(
        "export-subtree", help="Export a page and descendants to markdown"
    )
    export_parser.add_argument(
        "--root-page-id",
        required=True,
        help="Root page ID to export (example: canvas-xdtpgBB1FL)",
    )
    export_parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: coda-export-<root-page-id>)",
    )

    return parser.parse_args()


def resolve_auth(args: argparse.Namespace) -> tuple[str, str]:
    doc_id = args.doc_id or __import__("os").environ.get("CENTRAL_BRAIN_DOC_ID")
    token = args.token or __import__("os").environ.get("CODA_CENTRAL_BRAIN_TOKEN")
    if not doc_id:
        raise SystemExit("Missing doc ID. Pass --doc-id or set CENTRAL_BRAIN_DOC_ID.")
    if not token:
        raise SystemExit("Missing token. Pass --token or set CODA_CENTRAL_BRAIN_TOKEN.")
    return doc_id, token


def get_json(url: str, token: str, timeout: int, retries: int) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "coda-export-script/1.0",
    }
    backoff = 1.0

    for attempt in range(1, retries + 1):
        req = Request(url=url, headers=headers, method="GET")
        try:
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as err:
            status = getattr(err, "code", None)
            transient = status in (429, 500, 502, 503, 504)
            if transient and attempt < retries:
                time.sleep(backoff)
                backoff *= 2
                continue

            details = ""
            try:
                details = err.read().decode("utf-8", errors="replace")
            except Exception:
                details = ""
            raise SystemExit(f"HTTP error {status} for {url}\n{details}") from err
        except URLError as err:
            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise SystemExit(f"Network error for {url}: {err}") from err

    raise SystemExit(f"Failed after {retries} attempts: {url}")


def fetch_all_pages(doc_id: str, token: str, timeout: int, retries: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    query = urlencode({"limit": 500})
    url = f"{BASE_URL}/docs/{doc_id}/pages?{query}"
    while url:
        data = get_json(url=url, token=token, timeout=timeout, retries=retries)
        items.extend(data.get("items", []))
        url = data.get("nextPageLink")
    return items


def sanitize_name(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._ -]+", "", name or "")
    s = re.sub(r"\s+", " ", s).strip(" .")
    return s or "Untitled"


def item_to_markdown(style: str, text: str, ordered_index: int | None) -> str:
    text = text or ""
    if style == "h1":
        return f"# {text}"
    if style == "h2":
        return f"## {text}"
    if style == "h3":
        return f"### {text}"
    if style == "bulletedList":
        return f"- {text}"
    if style == "numberedList":
        return f"{ordered_index or 1}. {text}"
    if style == "checkboxList":
        return f"- [ ] {text}"
    if style == "blockQuote":
        return f"> {text}"
    if style == "code":
        return f"```\n{text}\n```"
    return text


def page_lineage(page_id: str, parent_map: dict[str, str | None]) -> list[str]:
    chain: list[str] = []
    cursor: str | None = page_id
    while cursor is not None:
        chain.append(cursor)
        cursor = parent_map.get(cursor)
    chain.reverse()
    return chain


def fetch_page_content(
    doc_id: str,
    token: str,
    page_id: str,
    timeout: int,
    retries: int,
) -> list[dict[str, Any]]:
    url = f"{BASE_URL}/docs/{doc_id}/pages/{page_id}/content"
    data = get_json(url=url, token=token, timeout=timeout, retries=retries)
    return data.get("items", [])


def export_subtree(args: argparse.Namespace, doc_id: str, token: str) -> None:
    root_page_id = args.root_page_id
    pages = fetch_all_pages(doc_id=doc_id, token=token, timeout=args.timeout, retries=args.retries)
    page_by_id = {page["id"]: page for page in pages}

    if root_page_id not in page_by_id:
        raise SystemExit(f"Root page ID not found: {root_page_id}")

    order: list[str] = []
    parent: dict[str, str | None] = {root_page_id: None}
    stack = [root_page_id]

    while stack:
        current = stack.pop()
        order.append(current)
        children = page_by_id.get(current, {}).get("children") or []
        for child in reversed(children):
            child_id = child["id"]
            parent[child_id] = current
            stack.append(child_id)

    out_dir = Path(args.out_dir or f"coda-export-{root_page_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, page_id in enumerate(order, start=1):
        page = page_by_id.get(page_id, {})
        page_name = page.get("name") or page_id

        lineage = page_lineage(page_id=page_id, parent_map=parent)

        page_dir = out_dir
        for ancestor_id in lineage[:-1]:
            ancestor_name = page_by_id.get(ancestor_id, {}).get("name", ancestor_id)
            page_dir /= f"{sanitize_name(ancestor_name)} [{ancestor_id}]"
        page_dir.mkdir(parents=True, exist_ok=True)

        file_path = page_dir / f"{sanitize_name(page_name)} [{page_id}].md"

        items = fetch_page_content(
            doc_id=doc_id,
            token=token,
            page_id=page_id,
            timeout=args.timeout,
            retries=args.retries,
        )

        lines: list[str] = []
        ordered_index = 0

        for item in items:
            item_content = item.get("itemContent") or {}
            style = item_content.get("style", "paragraph")
            text = item_content.get("content", "")

            if style == "numberedList":
                ordered_index += 1
            else:
                ordered_index = 0

            lines.append(
                item_to_markdown(
                    style=style,
                    text=text,
                    ordered_index=(ordered_index if style == "numberedList" else None),
                )
            )

        body = "\n\n".join(lines).strip()
        header = (
            f"# {page_name}\n\n"
            f"- Page ID: `{page_id}`\n"
            f"- Browser Link: {page.get('browserLink', '')}\n"
        )
        file_content = header + ("\n" + body if body else "\n")

        file_path.write_text(file_content, encoding="utf-8")
        print(f"[{idx}/{len(order)}] {file_path}")

    print(f"Export complete: {len(order)} files in {out_dir}")


def list_pages(args: argparse.Namespace, doc_id: str, token: str) -> None:
    pages = fetch_all_pages(doc_id=doc_id, token=token, timeout=args.timeout, retries=args.retries)
    contains = (args.contains or "").lower().strip()

    shown = 0
    for page in pages:
        page_id = page.get("id", "")
        page_name = page.get("name", "")

        if contains and contains not in page_name.lower():
            continue

        print(f"{page_id}\t{page_name}")
        shown += 1

    print(f"\nDisplayed {shown} pages (total in doc: {len(pages)})")


def main() -> None:
    args = parse_args()
    doc_id, token = resolve_auth(args)

    if args.command == "list-pages":
        list_pages(args=args, doc_id=doc_id, token=token)
        return

    if args.command == "export-subtree":
        export_subtree(args=args, doc_id=doc_id, token=token)
        return

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
