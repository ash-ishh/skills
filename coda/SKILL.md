---
name: coda
description: Export Coda document pages to local Markdown files. Use when a user wants to export, download, or extract content from Coda docs, list pages in a Coda document, or convert Coda page trees into Markdown. Triggers on tasks involving Coda API, Coda docs, or Coda page export.
---

# Coda Export

Export Coda pages and their descendants into local Markdown files using `scripts/coda_export.py`.

## Prerequisites

- Python 3.9+
- A Coda API token and doc ID, provided via CLI flags or env vars (`CENTRAL_BRAIN_DOC_ID`, `CODA_CENTRAL_BRAIN_TOKEN`)

## Commands

### List pages

```bash
python scripts/coda_export.py list-pages
```

Filter by name:

```bash
python scripts/coda_export.py list-pages --contains <search-term>
```

### Export a page subtree

```bash
python scripts/coda_export.py export-subtree --root-page-id <PAGE_ID>
```

With custom output directory:

```bash
python scripts/coda_export.py export-subtree --root-page-id <PAGE_ID> --out-dir <DIR>
```

Pass auth directly instead of env vars:

```bash
python scripts/coda_export.py --doc-id <DOC_ID> --token <TOKEN> export-subtree --root-page-id <PAGE_ID>
```

## Output

- One `.md` file per page
- Nested directories mirror the Coda page hierarchy
- Filenames include page IDs to avoid collisions

## Notes

- The script retries transient API/network failures automatically (configurable via `--retries`, default 6).
- HTTP timeout is configurable via `--timeout` (default 90s).
- Keep tokens out of git commits.
