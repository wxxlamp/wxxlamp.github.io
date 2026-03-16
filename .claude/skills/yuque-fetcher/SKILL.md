---
name: yuque-fetcher
description: Fetches Yuque (语雀) articles and saves them as Markdown with images re-hosted via img-uploader. Use when the user wants to download, save, export, or convert a Yuque article, or when they share a yuque.com URL and want its content extracted as Markdown.
license: Apache-2.0
metadata:
  author: wxx
  version: "1.0"
---

# Yuque Fetcher Skill

This skill fetches articles from Yuque (语雀) and converts them to local Markdown files. It uses Yuque's internal API to get clean Markdown content directly, and re-hosts images via the img-uploader skill.

## Prerequisites

1.  **Dependencies**: Python 3, Playwright, and requests.
    ```bash
    pip install -r .claude/skills/yuque-fetcher/requirements.txt
    playwright install chromium
    ```
2.  **img-uploader skill**: Must be configured if you want images re-hosted (see `.claude/skills/img-uploader/SKILL.md`). Use `--no-images` to skip image processing.

## First-Time Setup

On first run, a Chromium browser window will open for you to log in to Yuque manually. After login, the session is saved to `browser-data/storage_state.json` and reused for future requests.

To force re-login (e.g., if session expired):
```bash
python3 .claude/skills/yuque-fetcher/yuque-fetcher.py <url> --login
```

## Usage

```bash
python3 .claude/skills/yuque-fetcher/yuque-fetcher.py <yuque_url> [-o output_path] [--no-images] [--login]
```

### Arguments

- `<yuque_url>`: Yuque article URL (required), e.g. `https://www.yuque.com/user/repo/slug`
- `-o, --output`: Output Markdown file path (default: `./<article-title>.md`)
- `--no-images`: Skip image downloading and re-uploading, keep original URLs
- `--login`: Force re-login, ignoring any saved session

### Examples

**Fetch an article (default):**
```bash
python3 .claude/skills/yuque-fetcher/yuque-fetcher.py https://www.yuque.com/wangxingxing-f4sey/life/ka2yr80x894tbtgt
```

**Fetch with custom output path:**
```bash
python3 .claude/skills/yuque-fetcher/yuque-fetcher.py https://www.yuque.com/user/repo/slug -o ~/notes/article.md
```

**Fetch without image processing:**
```bash
python3 .claude/skills/yuque-fetcher/yuque-fetcher.py https://www.yuque.com/user/repo/slug --no-images
```

## Output

On success, the script saves a `.md` file and prints:
```text
Saved to ./文章标题.md
```

## How It Works

1. Authenticates via `_yuque_session` cookie (obtained through Playwright login)
2. Requests the article page HTML to extract `book_id` from embedded JSON
3. Calls Yuque's internal API (`/api/docs/{slug}?book_id=...&mode=markdown`) to get Markdown
4. Downloads article images, uploads via img-uploader, and replaces URLs
5. Saves the final Markdown to a local file
