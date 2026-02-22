---
name: img-uploader
description: Uploads images to image hosting services (supports Imgur, sm.ms, and GitHub + jsDelivr CDN). Imgur is the recommended and default provider.
license: Apache-2.0
metadata:
  author: crossoverJie
  version: "1.3"
---

# Image Uploader Skill

This skill allows uploading local image files to public image hosting services. It supports **Imgur** (recommended, default), **sm.ms**, and **GitHub** (with jsDelivr CDN acceleration).

## Prerequisites

1.  **Dependencies**: The skill requires Python 3 and the `requests` library.
    ```bash
    pip install -r .claude/skills/img-uploader/requirements.txt
    ```
2.  **Configuration**: An API token or client ID is required depending on the provider.

    **Imgur** (recommended, default):
    *   **Register**: Visit https://api.imgur.com/oauth2/addclient to register an application and get Client ID (no authentication required for anonymous uploads)
    *   **Config File**: `.claude/skills/img-uploader/config.json`
        ```json
        { "imgur_client_id": "YOUR_CLIENT_ID" }
        ```
    *   **Environment Variable**: `IMGUR_CLIENT_ID`
    *   **CLI Argument**: `--token`

    **sm.ms**:
    *   **Config File**: `.claude/skills/img-uploader/config.json`
        ```json
        { "smms_token": "YOUR_TOKEN" }
        ```
    *   **Environment Variable**: `SMMS_TOKEN`
    *   **CLI Argument**: `--token`

    **GitHub**:
    *   **Config File**: `.claude/skills/img-uploader/config.json`
        ```json
        {
            "github_token": "YOUR_GITHUB_TOKEN",
            "github_owner": "YOUR_GITHUB_USERNAME",
            "github_repo": "YOUR_IMAGE_REPO_NAME",
            "github_path": "images",
            "github_branch": "main",
            "github_cdn": "jsdelivr"
        }
        ```
    *   **Environment Variables**: `IMAGE_UPLOADER_GITHUB_TOKEN`, `IMAGE_UPLOADER_GITHUB_OWNER`, `IMAGE_UPLOADER_GITHUB_REPO`
    *   **CLI Argument**: `--token` (for token only)
    *   **CDN Options**:
        *   `"jsdelivr"` — `cdn.jsdelivr.net` (default, international)
        *   `"china"` — `jsd.cdn.zzko.cn` (China mirror)

    **Default Provider**: Set `default_provider` in `config.json` to `"smms"`, `"imgur"`, or `"github"`, or use the `IMAGE_UPLOADER_PROVIDER` environment variable.

    **Setup**: Copy `config.json.example` to `config.json` and fill in your tokens.

## Usage

To upload an image, run the Python script:

```bash
python3 .claude/skills/img-uploader/image-uploader.py <path_to_image>
```

### Examples

**Upload to Imgur (default, using config/env Client ID):**
```bash
python3 .claude/skills/img-uploader/image-uploader.py /Users/me/Pictures/screenshot.png
```

**Upload to sm.ms:**
```bash
python3 .claude/skills/img-uploader/image-uploader.py /Users/me/Pictures/screenshot.png --provider smms
```

**Upload to GitHub (jsDelivr CDN):**
```bash
python3 .claude/skills/img-uploader/image-uploader.py /Users/me/Pictures/screenshot.png --provider github
```

**Upload with explicit Client ID:**
```bash
python3 .claude/skills/img-uploader/image-uploader.py image.png --token "YOUR_IMGUR_CLIENT_ID"
```

**Upload to Imgur using env var:**
```bash
IMGUR_CLIENT_ID="your_id" python3 .claude/skills/img-uploader/image-uploader.py image.png
```

**Upload to GitHub using env vars:**
```bash
IMAGE_UPLOADER_GITHUB_TOKEN="your_token" IMAGE_UPLOADER_GITHUB_OWNER="user" IMAGE_UPLOADER_GITHUB_REPO="images" python3 .claude/skills/img-uploader/image-uploader.py image.png --provider github
```

## Output

The script outputs the result to stdout.

**Success (Imgur - default):**
```text
✅ Upload Successful!
URL: https://i.imgur.com/abcdefg.png
Delete Hash: AbCdEfGhIjK
```

**Success (sm.ms):**
```text
✅ Upload Successful!
URL: https://s2.loli.net/2023/01/01/abcdefg.jpg
Delete Link: https://sm.ms/delete/xyz123
Filename: screenshot.png
```

**Success (GitHub):**
```text
✅ Upload Successful!
CDN URL: https://cdn.jsdelivr.net/gh/user/repo@main/images/a1b2c3d4_screenshot.png
Raw URL: https://raw.githubusercontent.com/user/repo/main/images/a1b2c3d4_screenshot.png
```

**Already Exists (sm.ms):**
```text
⚠️  Image already exists.
URL: https://s2.loli.net/2023/01/01/abcdefg.jpg
```

**Failure:**
```text
❌ Upload Failed
Message: Unauthorized.
```