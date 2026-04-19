# uv

Use `uv` instead of `pip`, `python`, and `venv` for scripts and Python projects.

## Quick reference

```bash
uv run script.py
uv run --with requests script.py
uv run python -m ast foo.py >/dev/null
uv add requests
uv init --script foo.py
```

## Recommended patterns

### Run a script

```bash
uv run script.py
uv run script.py arg1 arg2
```

### Run with ad-hoc dependencies

```bash
uv run --with requests script.py
uv run --with requests --with rich script.py
```

### Verify syntax without creating `__pycache__`

```bash
uv run python -m ast script.py >/dev/null
```

### Create script metadata

```bash
uv init --script example.py --python 3.12
uv add --script example.py requests rich
```

## Inline script metadata

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "rich"]
# ///
```

Then run:

```bash
uv run example.py
```

## Build backend

For pure Python packages, use `uv_build`:

```toml
[build-system]
requires = ["uv_build>=0.9.28,<0.10.0"]
build-backend = "uv_build"
```

See also:

- [`scripts.md`](./scripts.md)
- [`build.md`](./build.md)
