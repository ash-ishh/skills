# Coda

Use this skill to export content from a Coda doc to local Markdown files.

It also maintains a local export index so repeat exports only update new or changed pages when the output directory already exists.

## What you need

- a Coda API token
- the Coda doc ID
- optionally, a page ID if you want a specific page or subtree

## How to generate a Coda API token

1. Open [Coda Account Settings](https://coda.io/account).
2. Scroll to **API Settings**.
3. Click **Generate API token**.
4. Give the token a name.
5. Under **Add a restriction**:
   - set **Type of restriction** to **Doc or table**
   - set **Type of access** to the access you want
   - paste the Coda doc link into **Doc or table to grant access to**
6. Click **Generate API token**.
7. Copy the token and save it somewhere safe.

## How to enable Developer Mode

1. Open **Account Settings** in Coda.
2. Scroll to **Developer tools**.
3. Turn on **Enable developer mode**.

This makes it easy to copy the exact IDs you need.

## How to copy the doc ID

1. Open the Coda doc.
2. Open the doc menu (`...`) near the top-right of the doc.
3. Click **Copy doc ID**.

This is the recommended way to get the doc ID.

## How to copy a page ID

1. In the page sidebar, open the `...` menu for a page.
2. Click **Copy page ID**.

Use this when you want the skill to work with a specific page or subtree.

## Environment variables

Set these before using the exporter:

```bash
export CODA_DOC_ID="your-doc-id"
export CODA_API_TOKEN="your-api-token"
```

## Known limitations

- Tables are not exported by the API into the generated Markdown files.
- Checklists are not exported in the correct Markdown checklist format.
- Images are not fetched and embedded into the exported Markdown files.

## Incremental updates

- The exporter keeps a local index file named `.coda-export-index.json` inside the export directory.
- On later runs, if the directory already exists, it compares each page's Coda `updatedAt` timestamp with the saved index.
- Only new or updated pages are re-exported.
- If a page was deleted in Coda, its local Markdown file is removed on the next sync and the index is updated.
- If `.coda-export-index.json` is deleted, the next export is treated as a full refresh and the index is rebuilt.
- Use `--overwrite` if you want to force a full rewrite.

## Notes

- Prefer **Copy doc ID** instead of manually parsing the URL.
- Developer Mode also exposes useful page-level IDs.
- Keep your API token out of git commits and shared screenshots.
