#!/usr/bin/env python3
"""Upload images using workspace-local credentials and return stable URLs."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

from workspace import find_workspace_root, load_config


def config_value(config: dict[str, Any], key: str, env_name: str, explicit: str | None = None) -> str:
    return str(explicit or os.environ.get(env_name) or config.get(key) or "")


def upload_imgur(path: Path, client_id: str) -> dict[str, Any]:
    if not client_id:
        raise ValueError("缺少 Imgur Client ID")
    with path.open("rb") as handle:
        response = requests.post(
            "https://api.imgur.com/3/image",
            headers={"Authorization": f"Client-ID {client_id}"},
            files={"image": handle},
            timeout=90,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success") or not payload.get("data", {}).get("link"):
        raise RuntimeError(str(payload.get("data", {}).get("error") or "Imgur upload failed"))
    return {
        "provider": "imgur",
        "url": payload["data"]["link"],
        "delete_hash": payload["data"].get("deletehash"),
    }


def upload_smms(path: Path, token: str) -> dict[str, Any]:
    if not token:
        raise ValueError("缺少 SM.MS token")
    with path.open("rb") as handle:
        response = requests.post(
            "https://sm.ms/api/v2/upload",
            headers={
                "Authorization": token,
                "User-Agent": "YuqueMultichannelPublisher/1.0",
            },
            files={"smfile": handle},
            timeout=90,
        )
    response.raise_for_status()
    payload = response.json()
    if payload.get("success"):
        data = payload.get("data", {})
        return {
            "provider": "smms",
            "url": data.get("url"),
            "delete_url": data.get("delete"),
        }
    if payload.get("code") == "image_repeated" and payload.get("images"):
        return {"provider": "smms", "url": payload["images"], "reused": True}
    raise RuntimeError(str(payload.get("message") or "SM.MS upload failed"))


def upload_github(path: Path, config: dict[str, Any], token: str) -> dict[str, Any]:
    if not token:
        raise ValueError("缺少 GitHub token")
    owner = config_value(config, "github_owner", "IMAGE_UPLOADER_GITHUB_OWNER")
    repository = config_value(config, "github_repo", "IMAGE_UPLOADER_GITHUB_REPO")
    if not owner or not repository:
        raise ValueError("缺少 github_owner 或 github_repo")
    branch = str(config.get("github_branch") or "main")
    remote_dir = str(config.get("github_path") or "images").strip("/")
    cdn_mode = str(config.get("github_cdn") or "jsdelivr")
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()[:8]
    remote_path = f"{remote_dir}/{digest}_{path.name}"
    response = requests.put(
        f"https://api.github.com/repos/{owner}/{repository}/contents/{remote_path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "message": f"Upload {path.name}",
            "content": base64.b64encode(content).decode("ascii"),
            "branch": branch,
        },
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    cdn_domain = "jsd.cdn.zzko.cn" if cdn_mode == "china" else "cdn.jsdelivr.net"
    return {
        "provider": "github",
        "url": f"https://{cdn_domain}/gh/{owner}/{repository}@{branch}/{remote_path}",
        "raw_url": payload.get("content", {}).get("download_url"),
    }


def upload_chevereto(path: Path, config: dict[str, Any], token: str) -> dict[str, Any]:
    base_url = config_value(config, "chevereto_url", "CHEVERETO_URL")
    if not token or not base_url:
        raise ValueError("缺少 Chevereto API key 或 chevereto_url")
    response = requests.post(
        f"{base_url.rstrip('/')}/api/1/upload",
        data={
            "key": token,
            "source": base64.b64encode(path.read_bytes()).decode("ascii"),
            "format": "json",
        },
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    image = payload.get("image", {})
    if payload.get("status_code") != 200 or not image.get("url"):
        raise RuntimeError(str(payload.get("error", {}).get("message") or "Chevereto upload failed"))
    return {"provider": "chevereto", "url": image["url"], "viewer_url": image.get("url_viewer")}


def upload_file(
    image_path: Path,
    *,
    provider: str | None = None,
    root: Path | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    workspace_root = root or find_workspace_root()
    config = load_config(workspace_root)
    selected = provider or os.environ.get("IMAGE_UPLOADER_PROVIDER") or str(config.get("image_provider") or "imgur")
    path = image_path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"图片不存在：{path}")
    if selected == "imgur":
        return upload_imgur(path, config_value(config, "imgur_client_id", "IMGUR_CLIENT_ID", token))
    if selected == "smms":
        return upload_smms(path, config_value(config, "smms_token", "SMMS_TOKEN", token))
    if selected == "github":
        return upload_github(path, config, config_value(config, "github_token", "IMAGE_UPLOADER_GITHUB_TOKEN", token))
    if selected == "chevereto":
        return upload_chevereto(path, config, config_value(config, "chevereto_api_key", "CHEVERETO_API_KEY", token))
    raise ValueError(f"不支持的图床：{selected}")


def main() -> None:
    parser = argparse.ArgumentParser(description="上传图片到工作区配置的图床")
    parser.add_argument("image_path")
    parser.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    parser.add_argument("--token")
    args = parser.parse_args()
    try:
        result = upload_file(Path(args.image_path), provider=args.provider, token=args.token)
    except (ValueError, RuntimeError, requests.RequestException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    print(json.dumps(result, ensure_ascii=False))
    print(f"URL: {result['url']}")


if __name__ == "__main__":
    main()
