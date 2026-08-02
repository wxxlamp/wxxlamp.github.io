#!/usr/bin/env python3
"""Fetch Yuque Markdown and re-host its images using this plugin."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any

import requests

from image_uploader import upload_file
from workspace import find_workspace_root, state_dir


YUQUE_BASE_URL = "https://www.yuque.com"
YUQUE_API_DOCS = "https://www.yuque.com/api/docs"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def parse_yuque_url(url: str) -> dict[str, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in {"www.yuque.com", "yuque.com"}:
        raise ValueError("只接受 https://www.yuque.com/... 文档地址")
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 3:
        raise ValueError("语雀地址格式应为 https://www.yuque.com/<user>/<repo>/<slug>")
    user, repo, slug = parts[:3]
    return {"namespace": f"{user}/{repo}", "slug": slug}


class YuqueSession:
    def __init__(self, storage_state: Path):
        self.storage_state = storage_state

    def cookies(self) -> dict[str, str]:
        if not self.storage_state.is_file():
            return {}
        payload = json.loads(self.storage_state.read_text(encoding="utf-8"))
        return {item["name"]: item["value"] for item in payload.get("cookies", [])}

    def cookie_header(self) -> str:
        return "; ".join(f"{key}={value}" for key, value in self.cookies().items())

    def validate(self) -> bool:
        if "_yuque_session" not in self.cookies():
            return False
        try:
            response = requests.get(
                f"{YUQUE_BASE_URL}/api/mine",
                headers={
                    "Cookie": self.cookie_header(),
                    "User-Agent": USER_AGENT,
                    "Referer": YUQUE_BASE_URL,
                },
                allow_redirects=False,
                timeout=15,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def login(self) -> None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError("缺少 playwright；请安装 requirements.txt 并执行 playwright install chromium") from None
        self.storage_state.parent.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            page.goto(f"{YUQUE_BASE_URL}/login")
            print("请在浏览器中登录语雀；检测到登录完成后窗口会自动关闭。")
            page.wait_for_url(lambda value: "/login" not in value, timeout=300_000)
            page.wait_for_load_state("networkidle")
            context.storage_state(path=str(self.storage_state))
            browser.close()

    def ensure(self, force_login: bool) -> None:
        # Public documents may be readable without cookies. Browser Controller is
        # the primary authenticated path; only open Playwright when explicitly
        # requested for this compatibility fetcher.
        if force_login:
            self.login()


class YuqueFetcher:
    def __init__(self, session: YuqueSession):
        self.session = session

    def headers(self) -> dict[str, str]:
        return {
            "Cookie": self.session.cookie_header(),
            "User-Agent": USER_AGENT,
            "Referer": YUQUE_BASE_URL,
        }

    def book_id(self, info: dict[str, str]) -> str:
        response = requests.get(
            f"{YUQUE_BASE_URL}/{info['namespace']}/{info['slug']}",
            headers=self.headers(),
            timeout=30,
        )
        if response.status_code in (302, 401, 403):
            raise RuntimeError(
                "语雀页面需要登录或不允许接口读取；请用 Browser Controller 复制 Markdown，"
                "再执行 pipeline.py ingest"
            )
        response.raise_for_status()
        match = re.search(r'decodeURIComponent\("(.+?)"\)', response.text)
        if match:
            try:
                payload = json.loads(urllib.parse.unquote(match.group(1)))
                value = payload.get("book", {}).get("id")
                if value:
                    return str(value)
            except json.JSONDecodeError:
                pass
        for pattern in (r'"book_id"\s*:\s*(\d+)', r'"book"\s*:\s*\{[^}]*"id"\s*:\s*(\d+)'):
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        raise RuntimeError("无法从语雀页面提取 book_id，页面结构或登录态可能已变化")

    def fetch(self, url: str) -> tuple[str, str]:
        info = parse_yuque_url(url)
        response = requests.get(
            f"{YUQUE_API_DOCS}/{info['slug']}",
            params={
                "book_id": self.book_id(info),
                "merge_dynamic_data": "false",
                "mode": "markdown",
            },
            headers=self.headers(),
            timeout=30,
        )
        if response.status_code in (302, 401):
            raise RuntimeError("语雀登录态已失效")
        response.raise_for_status()
        payload = response.json().get("data", {})
        markdown = payload.get("sourcecode", "")
        if not markdown:
            raise RuntimeError("语雀 API 返回空内容")
        return payload.get("title", "untitled"), markdown


def image_urls(markdown: str) -> list[str]:
    urls = set(re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", markdown))
    urls.update(re.findall(r'<img[^>]*?src=["\']?(https?://[^\s"\'?>]+)', markdown))
    return sorted(urls)


def download_image(url: str, cookies: dict[str, str], destination: Path) -> Path:
    headers = {"User-Agent": USER_AGENT, "Referer": YUQUE_BASE_URL}
    if cookies:
        headers["Cookie"] = "; ".join(f"{key}={value}" for key, value in cookies.items())
    response = requests.get(url, headers=headers, timeout=45, stream=True)
    response.raise_for_status()
    suffix = Path(urllib.parse.urlparse(url).path).suffix
    if not suffix:
        suffix = {
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "image/svg+xml": ".svg",
        }.get(response.headers.get("Content-Type", "").split(";")[0], ".png")
    path = destination / f"{hashlib_url(url)}{suffix}"
    with path.open("wb") as handle:
        for chunk in response.iter_content(8192):
            handle.write(chunk)
    return path


def hashlib_url(url: str) -> str:
    import hashlib

    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def migrate_images(
    markdown: str,
    *,
    session: YuqueSession,
    root: Path,
    provider: str | None,
) -> str:
    urls = image_urls(markdown)
    if not urls:
        return markdown
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="yuque-images-") as temp:
        destination = Path(temp)
        for index, url in enumerate(urls, 1):
            try:
                local = download_image(url, session.cookies(), destination)
                uploaded = upload_file(local, provider=provider, root=root)
                markdown = markdown.replace(url, uploaded["url"])
                print(f"[{index}/{len(urls)}] {uploaded['url']}")
            except (OSError, ValueError, RuntimeError, requests.RequestException) as exc:
                print(f"WARN: 图片迁移失败 {url}: {exc}", file=sys.stderr)
                failures.append(url)
    if failures:
        raise RuntimeError(f"{len(failures)} 张语雀图片迁移失败，未记录 fetched 检查点")
    return markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="拉取语雀 Markdown 并迁移图片")
    parser.add_argument("url")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--login", action="store_true")
    parser.add_argument("--no-images", action="store_true")
    parser.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    args = parser.parse_args()
    root = find_workspace_root()
    session = YuqueSession(state_dir(root) / "browser-data" / "storage_state.json")
    try:
        parse_yuque_url(args.url)
        session.ensure(args.login)
        title, markdown = YuqueFetcher(session).fetch(args.url)
        if not args.no_images:
            markdown = migrate_images(markdown, session=session, root=root, provider=args.provider)
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
    except (ValueError, RuntimeError, requests.RequestException, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"Title: {title}")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
