"""Workspace discovery and user-local configuration for the plugin."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


PLUGIN_STATE_NAME = "yuque-multichannel-publisher"
DEFAULT_CONFIG: dict[str, Any] = {
    "posts_dir": "source/_posts",
    "taxonomy_catalog": "source/_data/taxonomy.json",
    "reference_catalog": "source/_data/references.json",
    "content_projects_dir": "content-projects",
    "wechat_dir": "wechat",
    "rednote_dir": "rednote",
    "image_provider": "imgur",
    "cover_ratio": "21:9",
    "wechat_cover_ratio": "2.35:1",
    "lead_image_style": "ghibli-inspired",
    "wechat_similarity_min": 0.9,
    "rednote_images_min": 3,
    "rednote_images_max": 9,
    "md2wechat_executable": "md2wechat",
    "wechat_account": "",
    "xiaohongshu_skills_dir": "",
    "rednote_account": "",
    "rednote_cdp_host": "",
    "rednote_cdp_port": 9222,
    "rednote_allow_browser_launch": False,
    "github_path": "images",
    "github_branch": "main",
    "github_cdn": "jsdelivr",
}


def find_workspace_root(start: Path | None = None) -> Path:
    override = os.environ.get("YMP_WORKSPACE_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit(f"YMP_WORKSPACE_ROOT 不存在：{root}")
        return root

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (
            (candidate / ".codex" / PLUGIN_STATE_NAME / "config.json").is_file()
            or (candidate / "source" / "_posts").is_dir()
            or (candidate / "_config.yml").is_file()
            or (candidate / ".git").exists()
        ):
            return candidate
    raise SystemExit("找不到工作区；请进入项目目录或设置 YMP_WORKSPACE_ROOT")


def state_dir(root: Path) -> Path:
    return root / ".codex" / PLUGIN_STATE_NAME


def config_path(root: Path) -> Path:
    return state_dir(root) / "config.json"


def load_config(root: Path) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    path = config_path(root)
    if not path.is_file():
        return config
    try:
        custom = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"配置文件无法解析：{path}: {exc}") from None
    if not isinstance(custom, dict):
        raise SystemExit(f"配置文件顶层必须是对象：{path}")
    config.update(custom)
    return config


def configured_path(root: Path, config: dict[str, Any], key: str) -> Path:
    raw = str(config[key])
    path = Path(raw).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def posts_dir(root: Path, config: dict[str, Any] | None = None) -> Path:
    return configured_path(root, config or load_config(root), "posts_dir")
