#!/usr/bin/env python3
import os
import sys
import re
import json
import argparse
import tempfile
import subprocess
import urllib.parse
from pathlib import Path

import requests

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
BROWSER_DATA_DIR = os.path.join(SKILL_DIR, "browser-data")
STORAGE_STATE_FILE = os.path.join(BROWSER_DATA_DIR, "storage_state.json")
IMG_UPLOADER_SCRIPT = os.path.join(SKILL_DIR, "..", "img-uploader", "image-uploader.py")

YUQUE_BASE_URL = "https://www.yuque.com"
YUQUE_API_DOCS = "https://www.yuque.com/api/docs"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def parse_yuque_url(url):
    """Parse a Yuque URL into namespace and slug.

    Input:  https://www.yuque.com/wangxingxing-f4sey/life/ka2yr80x894tbtgt
    Output: {"user": "wangxingxing-f4sey", "repo": "life", "slug": "ka2yr80x894tbtgt",
             "namespace": "wangxingxing-f4sey/life"}
    """
    parsed = urllib.parse.urlparse(url)
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 3:
        raise ValueError(
            f"Invalid Yuque URL: {url}\n"
            "Expected format: https://www.yuque.com/<user>/<repo>/<slug>"
        )
    user, repo, slug = parts[0], parts[1], parts[2]
    return {
        "user": user,
        "repo": repo,
        "slug": slug,
        "namespace": f"{user}/{repo}",
    }


class YuqueSession:
    """Manages Yuque authentication via Playwright browser login."""

    def __init__(self, browser_data_dir=BROWSER_DATA_DIR, storage_state_file=STORAGE_STATE_FILE):
        self.browser_data_dir = browser_data_dir
        self.storage_state_file = storage_state_file

    def has_session(self):
        return os.path.exists(self.storage_state_file)

    def get_cookies(self):
        """Read saved storage state and return cookies as a dict."""
        if not self.has_session():
            return {}
        with open(self.storage_state_file, "r") as f:
            state = json.load(f)
        cookies = {}
        for c in state.get("cookies", []):
            cookies[c["name"]] = c["value"]
        return cookies

    def get_yuque_session_cookie(self):
        """Return the _yuque_session cookie value."""
        return self.get_cookies().get("_yuque_session", "")

    def get_cookie_header(self):
        """Return cookies formatted as a Cookie header string."""
        cookies = self.get_cookies()
        return "; ".join(f"{k}={v}" for k, v in cookies.items())

    def login(self):
        """Launch browser for manual login and save session state."""
        from playwright.sync_api import sync_playwright

        os.makedirs(self.browser_data_dir, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            page.goto(f"{YUQUE_BASE_URL}/login")
            print("Please log in to Yuque in the browser window...")
            print("The browser will close automatically after login is detected.")
            # Wait for navigation away from login page (max 5 minutes)
            page.wait_for_url(lambda url: "/login" not in url, timeout=300_000)
            page.wait_for_load_state("networkidle")
            context.storage_state(path=self.storage_state_file)
            print("Login successful! Session saved.")
            browser.close()

    def validate_session(self):
        """Test if the saved session is still valid by making a lightweight request."""
        if not self.has_session():
            return False
        cookies = self.get_cookies()
        if "_yuque_session" not in cookies:
            return False
        try:
            resp = requests.get(
                f"{YUQUE_BASE_URL}/api/mine",
                headers={
                    "Cookie": self.get_cookie_header(),
                    "User-Agent": USER_AGENT,
                    "Referer": YUQUE_BASE_URL,
                },
                allow_redirects=False,
                timeout=10,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def ensure_session(self, force_login=False):
        """Ensure a valid session exists, triggering login if needed."""
        if force_login:
            print("Force re-login requested.")
            self.login()
            return

        if self.has_session() and self.validate_session():
            return

        if self.has_session():
            print("Saved session has expired.")
        else:
            print("No saved session found.")
        self.login()


class YuqueFetcher:
    """Fetches article content from Yuque using the internal API."""

    def __init__(self, session: YuqueSession):
        self.session = session

    def _request_headers(self):
        return {
            "Cookie": self.session.get_cookie_header(),
            "User-Agent": USER_AGENT,
            "Referer": YUQUE_BASE_URL,
        }

    def _get_book_id(self, url_info):
        """Extract book_id from the article page's embedded JSON data."""
        page_url = f"{YUQUE_BASE_URL}/{url_info['namespace']}/{url_info['slug']}"
        resp = requests.get(page_url, headers=self._request_headers(), timeout=30)
        resp.raise_for_status()
        html = resp.text

        # Try decodeURIComponent pattern (used by yuque-crawl)
        match = re.search(r'decodeURIComponent\("(.+?)"\)', html)
        if match:
            try:
                decoded = urllib.parse.unquote(match.group(1))
                data = json.loads(decoded)
                book_id = data.get("book", {}).get("id")
                if book_id:
                    return str(book_id)
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback: search for book_id in the raw HTML/JSON
        match = re.search(r'"book_id"\s*:\s*(\d+)', html)
        if match:
            return match.group(1)

        match = re.search(r'"book"\s*:\s*\{[^}]*"id"\s*:\s*(\d+)', html)
        if match:
            return match.group(1)

        raise RuntimeError(
            "Could not extract book_id from page. "
            "The page structure may have changed, or the session may be invalid."
        )

    def fetch_article(self, url):
        """Fetch article content and return (title, markdown)."""
        url_info = parse_yuque_url(url)
        slug = url_info["slug"]

        print(f"Fetching article: {url}")
        print("Extracting book_id...", end=" ", flush=True)
        book_id = self._get_book_id(url_info)
        print(f"OK (book_id={book_id})")

        print("Fetching Markdown via API...", end=" ", flush=True)
        api_url = f"{YUQUE_API_DOCS}/{slug}"
        params = {
            "book_id": book_id,
            "merge_dynamic_data": "false",
            "mode": "markdown",
        }
        resp = requests.get(
            api_url,
            params=params,
            headers=self._request_headers(),
            timeout=30,
        )

        if resp.status_code in (401, 302):
            raise RuntimeError(
                "Session expired or unauthorized. Please re-run with --login."
            )
        resp.raise_for_status()

        data = resp.json().get("data", {})
        title = data.get("title", "untitled")
        markdown = data.get("sourcecode", "")

        if not markdown:
            raise RuntimeError("API returned empty content. The article may be restricted.")

        print("OK")
        print(f"Title: {title}")
        return title, markdown


class ImageProcessor:
    """Downloads article images, uploads via img-uploader, and replaces URLs."""

    def __init__(self, img_uploader_path=IMG_UPLOADER_SCRIPT):
        self.img_uploader_path = os.path.abspath(img_uploader_path)

    def _extract_image_urls(self, markdown):
        """Extract image URLs from Markdown content."""
        urls = set()
        # Markdown image syntax: ![alt](url)
        for match in re.finditer(r'!\[[^\]]*\]\((https?://[^)]+)\)', markdown):
            urls.add(match.group(1))
        # HTML img tags: <img src="url">
        for match in re.finditer(r'<img[^>]*?src=["\']?(https?://[^\s"\'?>]+)', markdown):
            urls.add(match.group(1))
        return list(urls)

    def _download_image(self, url, cookies, temp_dir):
        """Download an image to a temp directory and return the local path."""
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": YUQUE_BASE_URL,
        }
        # Build cookie header from dict
        if cookies:
            headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())

        resp = requests.get(url, headers=headers, timeout=30, stream=True)
        resp.raise_for_status()

        # Derive filename from URL (strip query params)
        parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed.path) or "image"
        # Ensure a file extension
        if "." not in filename:
            content_type = resp.headers.get("Content-Type", "")
            ext_map = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/gif": ".gif",
                "image/webp": ".webp",
                "image/svg+xml": ".svg",
            }
            filename += ext_map.get(content_type, ".png")

        local_path = os.path.join(temp_dir, filename)
        # Handle duplicate filenames
        counter = 1
        base, ext = os.path.splitext(local_path)
        while os.path.exists(local_path):
            local_path = f"{base}_{counter}{ext}"
            counter += 1

        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return local_path

    def _upload_image(self, local_path):
        """Upload an image using img-uploader and return the new URL."""
        result = subprocess.run(
            [sys.executable, self.img_uploader_path, local_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return None

        stdout = result.stdout
        # Parse "CDN URL: <url>" or "URL: <url>" from output
        for line in stdout.splitlines():
            line = line.strip()
            if line.startswith("CDN URL:"):
                return line.split("CDN URL:", 1)[1].strip()
            if line.startswith("URL:"):
                return line.split("URL:", 1)[1].strip()
        return None

    def process_images(self, markdown, cookies):
        """Download, upload, and replace all image URLs in the Markdown."""
        urls = self._extract_image_urls(markdown)
        if not urls:
            print("No images found.")
            return markdown

        print(f"Processing images ({len(urls)} found)...")
        url_map = {}
        temp_dir = tempfile.mkdtemp(prefix="yuque_images_")

        try:
            for i, url in enumerate(urls, 1):
                label = f"  [{i}/{len(urls)}]"
                # Download
                try:
                    print(f"{label} Downloading...", end=" ", flush=True)
                    local_path = self._download_image(url, cookies, temp_dir)
                    print("OK")
                except Exception as e:
                    print(f"FAILED ({e})")
                    continue

                # Upload
                try:
                    print(f"{label} Uploading...", end=" ", flush=True)
                    new_url = self._upload_image(local_path)
                    if new_url:
                        print(f"OK -> {new_url}")
                        url_map[url] = new_url
                    else:
                        print("FAILED (no URL in output)")
                except Exception as e:
                    print(f"FAILED ({e})")
        finally:
            # Cleanup temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        # Replace URLs in markdown
        for old_url, new_url in url_map.items():
            markdown = markdown.replace(old_url, new_url)

        replaced = len(url_map)
        skipped = len(urls) - replaced
        print(f"Images: {replaced} replaced, {skipped} skipped.")
        return markdown


def sanitize_filename(name):
    """Sanitize a string for use as a filename."""
    # Remove characters that are problematic in filenames
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    name = name.strip(". ")
    return name or "untitled"


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Yuque articles as Markdown with uploaded images."
    )
    parser.add_argument("url", help="Yuque article URL")
    parser.add_argument("-o", "--output", help="Output file path (default: <title>.md)")
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image downloading and uploading",
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Force re-login (ignore saved session)",
    )

    args = parser.parse_args()

    # Validate URL
    try:
        parse_yuque_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure session
    session = YuqueSession()
    try:
        session.ensure_session(force_login=args.login)
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Fetch article
    fetcher = YuqueFetcher(session)
    try:
        title, markdown = fetcher.fetch_article(args.url)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)

    # Process images
    if not args.no_images:
        if not os.path.exists(IMG_UPLOADER_SCRIPT):
            print(
                "Warning: img-uploader not found. Skipping image processing.\n"
                "  Configure img-uploader or use --no-images."
            )
        else:
            processor = ImageProcessor()
            cookies = session.get_cookies()
            markdown = processor.process_images(markdown, cookies)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = f"{sanitize_filename(title)}.md"

    # Write output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
