#!/usr/bin/env python3
"""Deterministic state and artifact handling for a resumable content pipeline."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as html_lib
import json
import os
import re
import socket
import shutil
import struct
import subprocess
import sys
import tempfile
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from editorial_quality import validate_editorial, validate_series_evidence, without_fences
from reference_links import reference_context
from publishing_policy import catalog_context, load_plan, title_for, english_enabled, validate_plan

from workspace import DEFAULT_CONFIG, configured_path, config_path, find_workspace_root, load_config, posts_dir, state_dir

STAGES = [
    "initialized",
    "fetched",
    "polished",
    "illustrated",
    "reviewed",
    "persisted",
    "drafted",
    "published",
]
CONTENT_STAGES = STAGES[: STAGES.index("drafted")]
DELIVERY_STATUSES = ("filled_for_review", "draft_saved", "published", "failed")
CHANNELS = ("blog", "wechat", "rednote")
EDIT_MODES = ("correction-only", "polish-expand")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((https://[^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
HTML_IMG_SRC_RE = re.compile(r"(?is)<img\b[^>]*?\bsrc\s*=\s*(['\"])(?P<src>.*?)\1")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n?", re.DOTALL)
SCRIPT_DIR = Path(__file__).resolve().parent
AI_TONE_CHECKS = {
    "template_opening",
    "empty_abstractions",
    "mechanical_transitions",
    "negative_parallelism",
    "rule_of_three",
    "excessive_parallelism",
    "repetitive_summaries",
    "generic_conclusion",
    "manufactured_punchline",
    "inflated_claims",
    "uniform_sentence_rhythm",
    "vague_attribution",
    "chatbot_artifacts",
}
AI_TONE_PATTERNS = {
    "模板化时代开场": re.compile(r"在当今.{0,12}(?:时代|背景下)|随着.{0,16}(?:发展|普及|演进)"),
    "结论套话": re.compile(r"综上所述|总而言之|由此可见|不难发现"),
    "空泛商业黑话": re.compile(r"赋能|抓手|闭环|底层逻辑|降本增效"),
    "机械提示语": re.compile(r"值得注意的是|需要指出的是|接下来(?:我们)?(?:将|来)"),
    "否定对照句": re.compile(r"不是.{0,30}而是|不(?:只是|仅仅|仅).{0,30}(?:更是|而是)"),
    "聊天机器人残留": re.compile(r"作为(?:一个|一名)?AI|希望以上(?:内容|回答)|如果你(?:还有|有)任何问题"),
}
REDNOTE_CROSS_REFERENCE_RE = re.compile(r"上一轮|下一轮|上[一篇文]|前文|见前文|接着上次")
SECTION_IMAGE_FIELDS = {"section_claim", "visual_type", "must_show", "avoid", "prompt", "review_status"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def validate_slug(slug: str) -> str:
    if not SLUG_RE.fullmatch(slug):
        raise SystemExit("project 必须是小写英文、数字和单连字符组成的 slug")
    return slug


def project_dir(repo: Path, slug: str) -> Path:
    config = load_config(repo)
    return configured_path(repo, config, "content_projects_dir") / validate_slug(slug)


def state_path(project: Path) -> Path:
    return project / ".codex" / "state.json"


def metadata_path(project: Path) -> Path:
    return project / "metadata.json"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"文件不存在：{path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON 无法解析：{path}: {exc}") from None


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def redact_adapter_secrets(text: str) -> str:
    """Keep adapter diagnostics useful without echoing credentials or tokens."""
    text = re.sub(
        r"(?i)((?:app_?secret|secret|access_token|token)=)[^&\s\"']+",
        r"\1<redacted>",
        text,
    )
    return re.sub(
        r'(?i)(["\'](?:app_?secret|secret|access_token|token)["\']\s*:\s*["\'])[^"\']+(["\'])',
        r"\1<redacted>\2",
        text,
    )


def redact_adapter_payload(value: Any) -> Any:
    if isinstance(value, str):
        return redact_adapter_secrets(value)
    if isinstance(value, list):
        return [redact_adapter_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_adapter_payload(item) for key, item in value.items()}
    return value


def adapter_error_message(payload: Any, stderr: str = "") -> str:
    if isinstance(payload, dict):
        message = str(payload.get("message") or payload.get("error") or "").strip()
    else:
        message = ""
    message = redact_adapter_secrets(message or stderr.strip() or "外部适配器返回未知错误")
    if "errcode=40164" in message or "not in whitelist" in message:
        match = re.search(r"invalid ip\s+([0-9a-fA-F:.]+)", message)
        ip = f"（{match.group(1)}）" if match else ""
        return f"微信公众号 API 拒绝当前出口 IP{ip}；请将它加入公众号 IP 白名单后重试"
    return message


def run_adapter_json(command: list[str], *, cwd: Path, timeout: int = 180) -> dict[str, Any]:
    """Run one adapter command to completion and parse its JSON contract safely."""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(
            "外部适配器命令超时，平台侧结果未知；请先检查素材库或草稿箱，避免直接重试产生重复项"
        ) from exc
    try:
        payload: Any = json.loads(result.stdout)
    except json.JSONDecodeError:
        message = redact_adapter_secrets(result.stderr.strip() or result.stdout.strip())
        raise SystemExit(f"外部适配器没有返回有效 JSON：{message or '空响应'}") from None
    if result.returncode or not isinstance(payload, dict) or payload.get("success") is False:
        raise SystemExit(f"外部适配器执行失败：{adapter_error_message(payload, result.stderr)}")
    return payload


def append_event(project: Path, event: dict[str, Any]) -> None:
    event = {"at": now_iso(), **event}
    path = project / ".codex" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_project(repo: Path, slug: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    project = project_dir(repo, slug)
    return project, read_json(state_path(project)), read_json(metadata_path(project))


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stage_rank(stage: str) -> int:
    try:
        return STAGES.index(stage)
    except ValueError:
        raise SystemExit(f"未知阶段 {stage}；可选：{', '.join(STAGES)}") from None


def update_stage(
    project: Path,
    state: dict[str, Any],
    stage: str,
    note: str = "",
    artifact: Path | None = None,
) -> None:
    stage_rank(stage)
    record: dict[str, Any] = {"stage": stage, "at": now_iso(), "note": note}
    if artifact:
        artifact = artifact.resolve()
        if not artifact.is_file():
            raise SystemExit(f"检查点产物不存在：{artifact}")
        record["artifact"] = str(artifact)
        record["sha256"] = file_digest(artifact)
    state["current_stage"] = stage
    state.setdefault("checkpoints", []).append(record)
    state["updated_at"] = record["at"]
    atomic_json(state_path(project), state)
    append_event(project, {"type": "checkpoint", **record})


def command_setup(args: argparse.Namespace) -> None:
    root = find_workspace_root()
    path = config_path(root)
    config = load_config(root) if path.exists() else dict(DEFAULT_CONFIG)
    for key in (
        "posts_dir",
        "content_projects_dir",
        "wechat_dir",
        "rednote_dir",
        "image_provider",
        "cover_ratio",
        "wechat_cover_ratio",
        "lead_image_style",
        "wechat_similarity_min",
        "rednote_images_min",
        "rednote_images_max",
        "md2wechat_executable",
        "wechat_account",
        "xiaohongshu_skills_dir",
        "rednote_account",
        "rednote_cdp_host",
        "rednote_cdp_port",
        "rednote_allow_browser_launch",
    ):
        value = getattr(args, key)
        if value is not None:
            config[key] = value
    if int(config["rednote_images_min"]) > int(config["rednote_images_max"]):
        raise SystemExit("rednote_images_min 不能大于 rednote_images_max")
    if not 0.5 <= float(config["wechat_similarity_min"]) <= 1:
        raise SystemExit("wechat_similarity_min 必须在 0.5–1 之间")
    atomic_json(path, config)
    posts_dir(root, config).mkdir(parents=True, exist_ok=True)
    print(path)


def command_init(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project = project_dir(repo, args.project)
    if state_path(project).exists():
        raise SystemExit(f"项目已存在：{project}\n使用 resume 继续，或在确认不再需要后手工归档旧项目")
    for relative in ("raw", "draft/rednote", "images", ".codex"):
        (project / relative).mkdir(parents=True, exist_ok=True)
    created = now_iso()
    config = load_config(repo)
    final_outputs = expected_outputs(repo, args.project)
    metadata = {
        "project": args.project,
        "yuque_url": args.yuque_url,
        "title": args.title or "",
        "edit_mode": args.edit_mode,
        "channels": list(dict.fromkeys(args.channels)),
        "cover_ratio": str(config.get("cover_ratio") or "21:9"),
        "wechat_cover_ratio": str(config.get("wechat_cover_ratio") or "2.35:1"),
        "lead_image_style": str(config.get("lead_image_style") or "ghibli-inspired"),
        "wechat_similarity_min": float(config.get("wechat_similarity_min", 0.9)),
        "description": "",
        "tags": [],
        "categories": [],
        "cover_image": {},
        "wechat_cover_image": {},
        "section_images": {},
        "rednote_images": {},
        "ai_tone_review": {},
        "editorial_contract_version": 2,
        "publishing_contract_version": 1,
        "reference_contract_version": 1,
        "related_posts_contract_version": 1,
        "wechat_links_contract_version": 1,
        "section_image_policy": "content-driven",
        "created_at": created,
    }
    state = {
        "schema_version": 2,
        "project": args.project,
        "repo_root": str(repo),
        "current_stage": "initialized",
        "created_at": created,
        "updated_at": created,
        "checkpoints": [{"stage": "initialized", "at": created, "note": "project created"}],
        "planned_outputs": {
            "blog": str(final_outputs["blog"]),
            "wechat": str(final_outputs["wechat_markdown"].parent),
            "rednote": str(final_outputs["rednote_root"]),
        },
        "outputs": {},
        "deliveries": {},
    }
    atomic_json(metadata_path(project), metadata)
    atomic_json(state_path(project), state)
    append_event(project, {"type": "initialized", "yuque_url": args.yuque_url})
    print(json.dumps({"staging_project": str(project), "final_targets": state["planned_outputs"]}, ensure_ascii=False, indent=2))


def command_resume(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    current = state.get("current_stage", "initialized")
    if current in CONTENT_STAGES:
        index = CONTENT_STAGES.index(current)
        next_stage = CONTENT_STAGES[index + 1] if index + 1 < len(CONTENT_STAGES) else "inspect-delivery-readiness"
    else:
        next_stage = "inspect-delivery-readiness"
    final_outputs = expected_outputs(repo, args.project)
    planned_outputs = state.get("planned_outputs") or {
        "blog": str(final_outputs["blog"]),
        "wechat": str(final_outputs["wechat_markdown"].parent),
        "rednote": str(final_outputs["rednote_root"]),
    }
    payload = {
        "project_dir": str(project),
        "current_stage": current,
        "next_stage": next_stage,
        "title": metadata.get("title", ""),
        "yuque_url": metadata.get("yuque_url", ""),
        "paths": {
            "raw": str(project / "raw" / "source.md"),
            "polished": str(project / "draft" / "polished.md"),
            "wechat": str(project / "draft" / "wechat.md"),
            "rednote": str(project / "draft" / "rednote"),
            "images": str(project / "images"),
        },
        "outputs": state.get("outputs", {}),
        "deliveries": state.get("deliveries", {}),
        "next_actions": delivery_next_actions(metadata, state),
        "final_targets": planned_outputs,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_checkpoint(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, _ = load_project(repo, args.project)
    artifact = Path(args.artifact) if args.artifact else None
    if artifact and not artifact.is_absolute():
        artifact = repo / artifact
    update_stage(project, state, args.stage, args.note or "", artifact)
    print(f"已记录 {args.stage}: {state_path(project)}")


def command_fetch(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    url = metadata.get("yuque_url")
    if not url:
        raise SystemExit("metadata.json 缺少 yuque_url")
    fetcher = SCRIPT_DIR / "yuque_fetcher.py"
    if not fetcher.is_file():
        raise SystemExit(f"找不到插件内置语雀拉取器：{fetcher}")
    output = project / "raw" / "source.md"
    command = [sys.executable, str(fetcher), url, "-o", str(output)]
    if args.login:
        command.append("--login")
    if args.no_images:
        command.append("--no-images")
    if args.provider:
        command.extend(["--provider", args.provider])
    result = subprocess.run(command, cwd=repo)
    if result.returncode:
        raise SystemExit(result.returncode)
    update_stage(project, state, "fetched", "Yuque source fetched", output)
    print(output)


def command_ingest(args: argparse.Namespace) -> None:
    """Persist Markdown obtained through the logged-in Browser Controller."""
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    source = Path(args.input).expanduser()
    if not source.is_absolute():
        source = (repo / source).resolve()
    if not source.is_file():
        raise SystemExit(f"浏览器导出的 Markdown 不存在：{source}")
    markdown = source.read_text(encoding="utf-8")
    if not markdown.strip():
        raise SystemExit("浏览器导出的 Markdown 为空")
    if args.migrate_images:
        from yuque_fetcher import YuqueSession, migrate_images

        session = YuqueSession(state_dir(repo) / "browser-data" / "storage_state.json")
        markdown = migrate_images(markdown, session=session, root=repo, provider=args.provider)
    output = project / "raw" / "source.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    if args.title:
        metadata["title"] = args.title
        atomic_json(metadata_path(project), metadata)
    update_stage(project, state, "fetched", "Yuque Markdown ingested from Browser Controller", output)
    print(output)


def parse_uploaded_url(output: str) -> str:
    for pattern in (
        r"^CDN URL:\s*(https://\S+)",
        r"^URL:\s*(https://\S+)",
        r"^Raw URL:\s*(https://\S+)",
    ):
        match = re.search(pattern, output, re.MULTILINE)
        if match:
            return match.group(1).strip()
    raise SystemExit("图片上传命令成功，但未能从输出解析 URL")


def image_dimensions(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:3] in (b"GIF",) and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    if data.startswith(b"\xff\xd8"):
        index = 2
        sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while index + 8 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            if marker in (0xD8, 0xD9):
                index += 2
                continue
            if index + 4 > len(data):
                break
            length = struct.unpack(">H", data[index + 2 : index + 4])[0]
            if marker in sof_markers and index + 9 <= len(data):
                height, width = struct.unpack(">HH", data[index + 5 : index + 9])
                return width, height
            index += 2 + length
    return None


def ratio_value(raw: str) -> float:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)\s*", raw)
    if not match or float(match.group(2)) == 0:
        raise SystemExit(f"无效图片比例：{raw}")
    return float(match.group(1)) / float(match.group(2))


def require_image_ratio(
    path: Path,
    kind: str,
    cover_ratio: str = "21:9",
    wechat_cover_ratio: str = "2.35:1",
) -> tuple[int, int] | None:
    dimensions = image_dimensions(path)
    expected = {
        "cover": ratio_value(cover_ratio),
        "wechat-cover": ratio_value(wechat_cover_ratio),
        "section": 16 / 9,
        "rednote": 3 / 4,
    }.get(kind)
    if expected is None:
        return dimensions
    if dimensions is None:
        raise SystemExit(f"无法读取 {path.suffix} 图片尺寸；封面和章节图请使用 PNG/JPEG")
    width, height = dimensions
    actual = width / height
    if abs(actual - expected) / expected > 0.01:
        labels = {
            "cover": cover_ratio,
            "wechat-cover": wechat_cover_ratio,
            "section": "16:9",
            "rednote": "3:4",
        }
        label = labels[kind]
        raise SystemExit(f"{kind} 图片尺寸为 {width}x{height}，不符合 {label}（允许 1% 误差）")
    return dimensions


def command_upload_image(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, _, metadata = load_project(repo, args.project)
    image = Path(args.file)
    if not image.is_absolute():
        image = (repo / image).resolve()
    if not image.is_file():
        raise SystemExit(f"图片不存在：{image}")
    if getattr(args, "language", "zh") == "en" and args.kind not in ("cover", "section"):
        raise SystemExit("英文图片只支持博客 cover / section，避免覆盖社交平台图片")
    configured_cover_ratio = str(metadata.get("cover_ratio") or "21:9")
    configured_wechat_cover_ratio = str(metadata.get("wechat_cover_ratio") or "2.35:1")
    dimensions = require_image_ratio(image, args.kind, configured_cover_ratio, configured_wechat_cover_ratio)
    uploader = SCRIPT_DIR / "image_uploader.py"
    command = [sys.executable, str(uploader), str(image)]
    if args.provider:
        command.extend(["--provider", args.provider])
    result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)
    url = parse_uploaded_url(result.stdout)
    record = {"url": url, "local": str(image), "uploaded_at": now_iso()}
    if dimensions:
        record["width"], record["height"] = dimensions
    if args.style:
        record["style"] = args.style
    if getattr(args, "language", "zh") == "en":
        record["ratio"] = configured_cover_ratio if args.kind == "cover" else "16:9"
        record["language"] = "en"
        metadata.setdefault("english_images", {})[args.key] = record
    elif args.kind == "cover":
        record["ratio"] = configured_cover_ratio
        record.setdefault("style", str(metadata.get("lead_image_style") or "ghibli-inspired"))
        metadata["cover_image"] = record
    elif args.kind == "wechat-cover":
        record["ratio"] = configured_wechat_cover_ratio
        metadata["wechat_cover_image"] = record
    elif args.kind == "section":
        record["ratio"] = "16:9"
        # Stable slot IDs allow several images in one section. Keep the prewritten
        # brief, but a new upload must not inherit approval of a previous image.
        previous = metadata.setdefault("section_images", {}).get(args.key, {})
        metadata["section_images"][args.key] = {**previous, **record, "review_status": "pending"}
    else:
        record["ratio"] = "3:4"
        metadata.setdefault("rednote_images", {}).setdefault(args.key, []).append(record)
    atomic_json(metadata_path(project), metadata)
    append_event(project, {"type": "image_uploaded", "kind": args.kind, "key": args.key, "url": url})
    print(f"RECORDED URL: {url}")


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def strip_front_matter(markdown: str) -> str:
    return FRONT_MATTER_RE.sub("", markdown, count=1).lstrip()


def selected_channels(metadata: dict[str, Any]) -> set[str]:
    raw = metadata.get("channels") or list(CHANNELS)
    channels = {str(value) for value in raw}
    unknown = channels - set(CHANNELS)
    if unknown:
        raise SystemExit(f"metadata.json 含未知渠道：{', '.join(sorted(unknown))}")
    return channels


def heading_numbered(level: int, title: str) -> bool:
    return re.match(rf"^(?:\d+\.){{{level}}}\s+\S", title) is not None


def normalized_prose(text: str, *, html: bool = False) -> str:
    """Normalize prose for channel-fidelity checks without rewriting it."""
    value = strip_front_matter(text)
    if html:
        value = re.sub(r"<[^>]+>", "", value)
        value = html_lib.unescape(value)
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"https?://\S+", "", value)
    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE)


def content_similarity(left: str, right: str, *, right_is_html: bool = False) -> float:
    if right_is_html:
        from wechat_links import MARKER, project_links
        if MARKER in right:
            from markdown_it import MarkdownIt
            left = project_links(MarkdownIt('commonmark', {'html': True}).enable('table').render(left))
            normalized_left = normalized_prose(left, html=True)
        else:
            normalized_left = normalized_prose(left)
    else:
        normalized_left = normalized_prose(left)
    normalized_right = normalized_prose(right, html=right_is_html)
    if not normalized_left and not normalized_right:
        return 1.0
    if not normalized_left or not normalized_right:
        return 0.0
    return SequenceMatcher(None, normalized_left, normalized_right, autojunk=False).ratio()


def rednote_round_number(path: Path) -> int | None:
    match = re.fullmatch(r"round([1-9]\d*)", path.parent.name)
    return int(match.group(1)) if match else None


def ai_tone_risks(markdown: str) -> list[str]:
    prose = without_fences(strip_front_matter(markdown))
    return [label for label, pattern in AI_TONE_PATTERNS.items() if pattern.search(prose)]


def validate_body_images(markdown: str, metadata: dict[str, Any]) -> list[str]:
    """Validate selected generated images, never impose an image count per heading."""
    from markdown_it import MarkdownIt
    from editorial_quality import html_content
    md = MarkdownIt('commonmark', {'html': True})
    tokens = md.parse(markdown)
    headings, images = [], []
    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            title = ''.join(html_content(md.renderer.render([tokens[index + 1]], md.options, {})).text)
            headings.append((title, int(token.tag[1]), token.map[0]))
        if token.type in ('inline', 'html_block') and token.map:
            parsed = html_content(md.renderer.render([token], md.options, {}))
            images.extend((url, token.map[0]) for url in parsed.images)
    records = metadata.get('section_images', {})
    if not isinstance(records, dict):
        return ['section_images 必须是以图片槽位 ID 为键的对象']
    errors, seen_urls = [], set()
    for slot, record in records.items():
        if not isinstance(record, dict):
            errors.append(f'正文配图“{slot}”记录必须是对象')
            continue
        # Old records keyed by heading remain readable; new IDs use section.
        section = record.get('section', slot)
        start, end = -1, len(markdown.splitlines())
        if section:
            matches = [(i, item) for i, item in enumerate(headings) if item[0] == section]
            if len(matches) != 1:
                errors.append(f'正文配图“{slot}”对应的标题不存在或不唯一：{section}')
                continue
            i, (_, level, start) = matches[0]
            end = next((line for _, depth, line in headings[i + 1:] if depth <= level), end)
        url = record.get('url')
        if not isinstance(url, str) or not url.startswith('https://'):
            errors.append(f'正文配图“{slot}”需要公开 HTTPS URL')
        elif not any(src == url and start < line < end for src, line in images):
            errors.append(f'正文配图“{slot}”必须出现在指定章节内（无章节时在正文内）')
        elif url in seen_urls:
            errors.append(f'正文配图“{slot}”重复登记同一 URL；跨节共用图只登记一次')
        if isinstance(url, str):
            seen_urls.add(url)
        if record.get('ratio') != '16:9' or record.get('review_status') != 'passed':
            errors.append(f'正文配图“{slot}”需要 16:9 比例和视觉复审')
        if SECTION_IMAGE_FIELDS - set(record) or not isinstance(record.get('must_show'), list) or len(record.get('must_show', [])) < 2:
            errors.append(f'正文配图“{slot}”缺少完整视觉 brief，must_show 至少需要两个具体元素或关系')
        if (metadata.get('section_image_policy') == 'content-driven' or 'section' in record) and not str(record.get('placement_reason', '')).strip():
            errors.append(f'正文配图“{slot}”缺少 placement_reason')
    return errors


def validate_draft(project: Path, metadata: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    polished_path = project / "draft" / "polished.md"
    if not polished_path.is_file():
        return [f"缺少 {polished_path}"], warnings
    polished = strip_front_matter(polished_path.read_text(encoding="utf-8"))
    channels = selected_channels(metadata)
    if "{{" in polished or "}}" in polished:
        errors.append("polished.md 仍含未替换占位符")
    for field in ("title", "description"):
        if not str(metadata.get(field, "")).strip():
            errors.append(f"metadata.json 缺少 {field}")
    if metadata.get("edit_mode") == "polish-expand" and metadata.get("editorial_contract_version") != 2:
        tone_review = metadata.get("ai_tone_review")
        if not isinstance(tone_review, dict) or tone_review.get("status") != "passed":
            errors.append("polish-expand 必须由 AI 完成去 AI 味复审，并记录 ai_tone_review.status=passed")
        else:
            checks = {str(value) for value in tone_review.get("checks", [])}
            missing_checks = AI_TONE_CHECKS - checks
            if missing_checks:
                errors.append(f"ai_tone_review 缺少检查项：{', '.join(sorted(missing_checks))}")
            fingerprint = str(tone_review.get("corpus_fingerprint", ""))
            if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
                errors.append("ai_tone_review 必须记录当前 author-voice.md 的 64 位语料指纹")
            voice_reference = str(tone_review.get("voice_reference", ""))
            expected_voice_path = ".codex/yuque-multichannel-publisher/style-profiles/author-voice.md"
            if not voice_reference.endswith(expected_voice_path):
                errors.append("ai_tone_review 必须记录工作区 .codex 中的 author-voice.md，个人语气不得来自插件目录")
        for risk in ai_tone_risks(polished):
            warnings.append(f"去 AI 味复审仍检测到“{risk}”风险；由 AI 结合上下文确认或重写")
    cover_url = metadata.get("cover_image", {}).get("url", "")
    if not cover_url:
        errors.append("metadata.json 缺少 cover_image.url")
    elif not str(cover_url).startswith("https://"):
        errors.append("metadata.json 的 cover_image.url 必须是公开 HTTPS 地址")
    elif cover_url not in "\n".join(polished.splitlines()[:20]):
        errors.append("封面 URL 必须出现在 polished.md 开头 20 行内")
    expected_cover_ratio = str(metadata.get("cover_ratio") or "21:9")
    if metadata.get("cover_image", {}).get("ratio") != expected_cover_ratio:
        errors.append(f"metadata.json 的 cover_image.ratio 必须为 {expected_cover_ratio}")
    expected_lead_style = str(metadata.get("lead_image_style") or "ghibli-inspired")
    if metadata.get("cover_image", {}).get("style") != expected_lead_style:
        errors.append(f"正文首图必须记录 style={expected_lead_style}，并由 AI review 实际画面")
    structural_prose = without_fences(polished)
    for line in structural_prose.splitlines():
        any_heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if any_heading and not heading_numbered(len(any_heading.group(1)), any_heading.group(2)):
            errors.append(f"标题“{any_heading.group(2)}”缺少 {len(any_heading.group(1))} 级数字序号")
    errors.extend(validate_body_images(polished, metadata))
    if "wechat" in channels:
        wechat_cover = metadata.get("wechat_cover_image", {})
        expected_wechat_ratio = str(metadata.get("wechat_cover_ratio") or "2.35:1")
        if not str(wechat_cover.get("url", "")).startswith("https://"):
            errors.append("metadata.json 缺少微信公众号公开 HTTPS 封面地址")
        if wechat_cover.get("ratio") != expected_wechat_ratio:
            errors.append(f"微信公众号封面比例必须为 {expected_wechat_ratio}")
        if not 8 <= len(str(wechat_cover.get("title", "")).strip()) <= 14:
            errors.append("微信公众号封面必须记录 8–14 字短标题")
        if not str(wechat_cover.get("title_safe_area", "")).strip():
            errors.append("微信公众号封面必须记录标题安全区")
        if wechat_cover.get("review_status") != "passed":
            errors.append("微信公众号封面标题必须经过 AI 逐字复审")
        wechat = project / "draft" / "wechat.md"
        wechat_text = ""
        if not wechat.is_file():
            errors.append(f"缺少 {wechat}")
        else:
            wechat_text = wechat.read_text(encoding="utf-8")
            if "{{" in wechat_text:
                errors.append("wechat.md 仍含未替换占位符")
            similarity_min = float(metadata.get("wechat_similarity_min", 0.9))
            similarity = content_similarity(polished, wechat_text)
            if similarity < similarity_min:
                errors.append(
                    f"wechat.md 与博客正文相似度为 {similarity:.1%}，低于 {similarity_min:.0%}；"
                    "公众号只应做轻量平台适配，不得重写或删减主体内容"
                )
        wechat_html = project / "draft" / "wechat.html"
        if not wechat_html.is_file():
            errors.append(f"缺少 AI 排版产物 {wechat_html}")
        else:
            html = wechat_html.read_text(encoding="utf-8", errors="replace").lower()
            if "{{" in html:
                errors.append("wechat.html 仍含未替换占位符")
            if any(token in html for token in ("<script", "<link", "<style")):
                errors.append("wechat.html 只能使用行内样式，不得包含 script、link 或 style 标签")
            if "style=" not in html:
                errors.append("wechat.html 缺少 AI 生成的行内样式")
            if wechat_text:
                html_similarity = content_similarity(wechat_text, wechat_html.read_text(encoding="utf-8"), right_is_html=True)
                if html_similarity < 0.9:
                    errors.append(
                        f"wechat.html 与 wechat.md 的正文相似度为 {html_similarity:.1%}，排版时不得改写内容"
                    )
    if "rednote" in channels:
        rounds = sorted((project / "draft" / "rednote").glob("round*/post.md"), key=lambda p: rednote_round_number(p) or 0)
        config = load_config(find_workspace_root(project))
        minimum_images = int(config.get("rednote_images_min", 3))
        maximum_images = int(config.get("rednote_images_max", 5))
        if not rounds:
            errors.append("小红书至少需要一个由 AI 内容分析得出的 roundN/post.md")
        round_numbers = [rednote_round_number(path) for path in rounds]
        if any(number is None for number in round_numbers):
            errors.append("小红书目录必须使用 round1、round2……格式")
        elif round_numbers != list(range(1, len(round_numbers) + 1)):
            errors.append("小红书轮次必须从 round1 开始连续编号，不能跳号")
        series_plan = project / "draft" / "rednote" / "series-plan.json"
        if not series_plan.is_file():
            errors.append(f"缺少小红书系列策划：{series_plan}")
        else:
            plan = read_json(series_plan)
            if metadata.get("editorial_contract_version") == 2:
                errors.extend(validate_series_evidence(plan, polished))
            planned_rounds = plan.get("rounds") if isinstance(plan, dict) else None
            if not isinstance(planned_rounds, list) or not planned_rounds:
                errors.append("series-plan.json 至少需要一个由 AI 规划的轮次")
            elif len(planned_rounds) != len(rounds):
                errors.append("series-plan.json 的 rounds 必须与实际 roundN 目录一一对应")
            else:
                if not str(plan.get("round_count_reason", "")).strip():
                    errors.append("series-plan.json 必须说明 AI 选择当前轮数的 round_count_reason")
                planned_names = [str(item.get("round", "")) for item in planned_rounds if isinstance(item, dict)]
                expected_names = [path.parent.name for path in rounds]
                if planned_names != expected_names:
                    errors.append("series-plan.json 的轮次顺序必须与 roundN 目录一致")
                angles = [str(item.get("angle", "")).strip() for item in planned_rounds if isinstance(item, dict)]
                if len(angles) != len(rounds) or any(not angle for angle in angles):
                    errors.append("series-plan.json 每轮必须填写独立 angle")
                elif len(set(angles)) != len(angles):
                    errors.append("series-plan.json 各轮 angle 不得重复")
                for item in planned_rounds:
                    if not isinstance(item, dict):
                        continue
                    round_name = str(item.get("round", "该轮"))
                    for field in ("subject", "target_reader", "core_viewpoint", "context_brief", "reader_promise", "hook"):
                        if not str(item.get(field, "")).strip():
                            errors.append(f"series-plan.json 的 {round_name} 缺少 {field}")
                    image_plan = item.get("image_plan")
                    if not isinstance(image_plan, list) or not minimum_images <= len(image_plan) <= maximum_images:
                        errors.append(
                            f"series-plan.json 的 {round_name}.image_plan 需要 {minimum_images}–{maximum_images} 项"
                        )
        for round_path in rounds:
            text = strip_front_matter(round_path.read_text(encoding="utf-8"))
            if "{{" in text:
                errors.append(f"{round_path.parent.name} 仍含未替换占位符")
            if REDNOTE_CROSS_REFERENCE_RE.search(text):
                errors.append(f"{round_path.parent.name} 含跨轮指代，必须改为独立可读的上下文")
            visible = re.sub(r"[#*`>\[\]()!https:/._-]", "", text)
            if len(visible) > 1200:
                warnings.append(f"{round_path.parent.name} 可见字符约 {len(visible)}，建议压缩到 900 以内")
            image_count = len(IMAGE_RE.findall(text))
            if not minimum_images <= image_count <= maximum_images:
                errors.append(
                    f"{round_path.parent.name} 需要 {minimum_images}–{maximum_images} 张 HTTPS 配图，当前 {image_count} 张"
                )
            title_match = re.search(r"(?m)^#\s+([^#].+)$", text)
            if not title_match:
                warnings.append(f"{round_path.parent.name} 建议用一级标题作为发布标题")
            elif len(title_match.group(1).strip()) > 20:
                warnings.append(f"{round_path.parent.name} 标题超过 20 字，建议缩短")
            hashtag_count = len(re.findall(r"(?<!\S)#[^\s#]+", text))
            if not 5 <= hashtag_count <= 8:
                errors.append(f"{round_path.parent.name} 需要 5–8 个话题标签，当前 {hashtag_count} 个")
            cards_path = round_path.parent / "cards.json"
            if not cards_path.is_file():
                errors.append(f"{round_path.parent.name} 缺少 cards.json 卡片叙事")
                continue
            cards_payload = read_json(cards_path)
            cards = cards_payload.get("cards") if isinstance(cards_payload, dict) else None
            if not isinstance(cards, list) or not minimum_images <= len(cards) <= maximum_images:
                errors.append(
                    f"{round_path.parent.name}/cards.json 需要 {minimum_images}–{maximum_images} 张卡片"
                )
                continue
            for expected_index, card in enumerate(cards, start=1):
                if not isinstance(card, dict):
                    errors.append(f"{round_path.parent.name}/cards.json 第 {expected_index} 项必须是对象")
                    continue
                if card.get("index") != expected_index:
                    errors.append(f"{round_path.parent.name}/cards.json 卡片编号必须从 1 连续排列")
                for field in ("role", "headline", "body", "visual_strategy", "material_ref"):
                    if not str(card.get(field, "")).strip():
                        errors.append(f"{round_path.parent.name}/cards.json 第 {expected_index} 张缺少 {field}")
                if len(str(card.get("body", "")).strip()) > 80:
                    errors.append(f"{round_path.parent.name}/cards.json 第 {expected_index} 张正文超过 80 个汉字")
    if metadata.get("editorial_contract_version") == 2:
        errors.extend(validate_editorial(project, metadata, channels))
    else:
        warnings.append("旧项目尚未启用编辑契约 v2；继续加工时按 editorial-review.md 升级")
    if metadata.get("publishing_contract_version") == 1:
        errors.extend(validate_plan(project, metadata, find_workspace_root(project)))
    return errors, warnings


def expected_outputs(repo: Path, slug: str) -> dict[str, Path]:
    config = load_config(repo)
    return {
        "blog": posts_dir(repo, config) / f"{slug}.md",
        "blog_en": posts_dir(repo, config) / "en" / f"{slug}.md",
        "wechat_markdown": configured_path(repo, config, "wechat_dir") / slug / "article.md",
        "wechat_html": configured_path(repo, config, "wechat_dir") / slug / "article.html",
        "rednote_root": configured_path(repo, config, "rednote_dir") / slug,
    }


def validate_materialized(repo: Path, slug: str, metadata: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    outputs = expected_outputs(repo, slug)
    channels = selected_channels(metadata)
    required = []
    if "blog" in channels:
        required.append("blog")
        if english_enabled(project_dir(repo, slug), metadata): required.append("blog_en")
    if "wechat" in channels:
        required.extend(("wechat_markdown", "wechat_html"))
    for name in required:
        if not outputs[name].is_file():
            errors.append(f"缺少 {name}: {outputs[name]}")
    rounds = sorted(outputs["rednote_root"].glob("round*/post.md"), key=lambda p: rednote_round_number(p) or 0) if "rednote" in channels else []
    if "rednote" in channels:
        if not rounds:
            errors.append(f"小红书最终目录至少需要一个 AI 规划轮次：{outputs['rednote_root']}")
        round_numbers = [rednote_round_number(path) for path in rounds]
        if round_numbers != list(range(1, len(round_numbers) + 1)):
            errors.append(f"小红书最终目录轮次不连续：{outputs['rednote_root']}")
        if not (outputs["rednote_root"] / "series-plan.json").is_file():
            errors.append(f"缺少小红书系列策划：{outputs['rednote_root'] / 'series-plan.json'}")
        for round_path in rounds:
            if not (round_path.parent / "cards.json").is_file():
                errors.append(f"小红书最终目录缺少卡片叙事：{round_path.parent / 'cards.json'}")
    if "blog" in channels and outputs["blog"].is_file() and not outputs["blog"].read_text(encoding="utf-8").startswith("---\n"):
        errors.append("博客文章缺少 front matter")
    if metadata.get("editorial_contract_version") == 2:
        project = project_dir(repo, slug)
        draft_errors, draft_warnings = validate_draft(project, metadata)
        errors.extend(draft_errors)
        warnings.extend(draft_warnings)
        pairs = []
        if "blog" in channels:
            pairs.append((project/"draft/polished.md", outputs["blog"], True))
            if english_enabled(project, metadata):
                pairs.append((project/"draft/english.md", outputs["blog_en"], True))
            elif metadata.get("publishing_contract_version") == 1 and outputs["blog_en"].exists():
                errors.append("英文版已跳过但最终目录存在旧译稿，请先明确归档旧稿")
        if "wechat" in channels:
            pairs += [(project/"draft/wechat.md", outputs["wechat_markdown"], True),
                      (project/"draft/wechat.html", outputs["wechat_html"], False)]
        if "rednote" in channels:
            source = project/"draft/rednote"
            expected = {p.relative_to(source) for p in source.glob("round*/*") if p.name in {"post.md", "cards.json"}}
            actual = {p.relative_to(outputs["rednote_root"]) for p in outputs["rednote_root"].glob("round*/*") if p.name in {"post.md", "cards.json"}}
            if actual != expected:
                errors.append("小红书最终轮次/卡片与当前已审阅草稿不一致，先归档过时轮次并重新物化")
            pairs += [(source/name, outputs["rednote_root"]/name, False) for name in expected | {Path("series-plan.json")}]
        for source, target, frontmatter in pairs:
            if source.is_file() and target.is_file():
                left, right = source.read_text(), target.read_text()
                if frontmatter:
                    left, right = strip_front_matter(left), strip_front_matter(right)
                if left.rstrip() != right.rstrip():
                    errors.append(f"最终产物与已审阅草稿不一致，请重新物化：{target}")
    return errors, warnings


def delivery_next_actions(metadata: dict[str, Any], state: dict[str, Any]) -> list[dict[str, str]]:
    """Return target-aware actions instead of pretending delivery is one linear stage."""
    actions: list[dict[str, str]] = []
    current = str(state.get("current_stage", "initialized"))
    if current in CONTENT_STAGES and CONTENT_STAGES.index(current) < CONTENT_STAGES.index("persisted"):
        return [{"target": "content", "action": f"complete-{CONTENT_STAGES[CONTENT_STAGES.index(current) + 1]}"}]
    deliveries = state.get("deliveries") if isinstance(state.get("deliveries"), dict) else {}
    for channel in sorted(selected_channels(metadata)):
        if channel == "blog":
            actions.append({"target": "blog", "action": "review-repository-diff"})
            continue
        channel_records = deliveries.get(channel) if isinstance(deliveries.get(channel), dict) else {}
        statuses = {
            str(record.get("status", ""))
            for record in channel_records.values()
            if isinstance(record, dict)
        }
        action = "review-publish-readiness"
        if "published" in statuses:
            action = "verify-published-result"
        elif "draft_saved" in statuses:
            action = "review-platform-draft"
        elif "filled_for_review" in statuses:
            action = "save-platform-draft-manually"
        actions.append({"target": channel, "action": action})
    return actions


def resolve_executable(raw: str) -> str | None:
    candidate = Path(raw).expanduser()
    if candidate.parent != Path("."):
        return str(candidate.resolve()) if candidate.is_file() else None
    return shutil.which(raw)


def external_directory(repo: Path, raw: str) -> Path | None:
    if not raw.strip():
        return None
    candidate = Path(raw).expanduser()
    path = candidate.resolve() if candidate.is_absolute() else (repo / candidate).resolve()
    return path if path.is_dir() else None


def resolve_project_image(repo: Path, project: Path, raw: str) -> Path | None:
    if not raw.strip():
        return None
    candidate = Path(raw).expanduser()
    candidates = [candidate] if candidate.is_absolute() else [repo / candidate, project / candidate]
    for path in candidates:
        resolved = path.resolve()
        if resolved.is_file():
            return resolved
    matches = list((project / "images").rglob(candidate.name)) if candidate.name else []
    return matches[0].resolve() if len(matches) == 1 else None


def metadata_image_sources(repo: Path, project: Path, metadata: dict[str, Any]) -> dict[str, Path]:
    """Map published image URLs back to their existing local source files."""
    records: list[dict[str, Any]] = []
    for key in ("cover_image", "wechat_cover_image"):
        value = metadata.get(key)
        if isinstance(value, dict):
            records.append(value)
    sections = metadata.get("section_images")
    if isinstance(sections, dict):
        records.extend(value for value in sections.values() if isinstance(value, dict))
    mapping: dict[str, Path] = {}
    for record in records:
        url = str(record.get("url") or "").strip()
        local = resolve_project_image(repo, project, str(record.get("local") or ""))
        if url and local:
            mapping[url] = local
    return mapping


def wechat_material_cache_path(project: Path) -> Path:
    return project / ".codex" / "wechat-materials.json"


def load_wechat_material_cache(project: Path) -> dict[str, Any]:
    path = wechat_material_cache_path(project)
    if not path.is_file():
        return {"version": 1, "items": {}}
    payload = read_json(path)
    if not isinstance(payload.get("items"), dict):
        return {"version": 1, "items": {}}
    return payload


def adapter_account_flags(account: str) -> list[str]:
    return ["--wechat-account", account] if account else []


def upload_wechat_material(
    executable: str,
    *,
    repo: Path,
    project: Path,
    account: str,
    source: str,
    local_path: Path | None = None,
) -> dict[str, str]:
    cache = load_wechat_material_cache(project)
    if local_path:
        cache_key = f"file:{file_digest(local_path)}"
        command = [executable, "upload_image", str(local_path), *adapter_account_flags(account), "--json"]
    else:
        cache_key = "url:" + hashlib.sha256(source.encode("utf-8")).hexdigest()
        command = [executable, "download_and_upload", source, *adapter_account_flags(account), "--json"]
    cached = cache["items"].get(cache_key)
    if isinstance(cached, dict) and cached.get("media_id") and cached.get("wechat_url"):
        return {"media_id": str(cached["media_id"]), "wechat_url": str(cached["wechat_url"])}
    payload = run_adapter_json(command, cwd=repo)
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    media_id = str(data.get("media_id") or "").strip()
    wechat_url = str(data.get("wechat_url") or "").strip()
    if not media_id or not wechat_url:
        raise SystemExit("md2wechat 上传素材成功，但响应缺少 media_id 或 wechat_url")
    record = {"media_id": media_id, "wechat_url": wechat_url, "source": source, "at": now_iso()}
    cache["items"][cache_key] = record
    atomic_json(wechat_material_cache_path(project), cache)
    return {"media_id": media_id, "wechat_url": wechat_url}


def prepare_wechat_html(
    executable: str,
    *,
    repo: Path,
    project: Path,
    metadata: dict[str, Any],
    account: str,
    html: str,
) -> str:
    local_sources = metadata_image_sources(repo, project, metadata)
    replacements: dict[str, str] = {}
    for match in HTML_IMG_SRC_RE.finditer(html):
        source = match.group("src").strip()
        if not source or source in replacements:
            continue
        if source.startswith("http://mmbiz.qpic.cn/") or source.startswith("https://mmbiz.qpic.cn/"):
            replacements[source] = source
            continue
        local_path = local_sources.get(source)
        if not local_path and not source.startswith(("http://", "https://")):
            raise SystemExit(f"公众号 HTML 图片既不是可用本地文件，也不是远程 URL：{source}")
        material = upload_wechat_material(
            executable,
            repo=repo,
            project=project,
            account=account,
            source=source,
            local_path=local_path,
        )
        replacements[source] = material["wechat_url"]

    def replace(match: re.Match[str]) -> str:
        source = match.group("src").strip()
        replacement = replacements.get(source, source)
        return match.group(0).replace(match.group("src"), replacement, 1)

    return HTML_IMG_SRC_RE.sub(replace, html)


def content_metrics(project: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    path = project / "draft" / "polished.md"
    if not path.is_file():
        return {"available": False}
    markdown = strip_front_matter(path.read_text(encoding="utf-8"))
    visible = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    visible = re.sub(r"[#>*_`\[\]()!-]", "", visible)
    headings = re.findall(r"(?m)^(#{1,6})\s+(.+)$", markdown)
    return {
        "available": True,
        "visible_characters": len(re.sub(r"\s+", "", visible)),
        "headings": len(headings),
        "remote_images": len(IMAGE_RE.findall(markdown)),
        "description_characters": len(str(metadata.get("description", "")).strip()),
        "ai_tone_phrase_risks": ai_tone_risks(markdown),
    }


def target_readiness(repo: Path, project: Path, metadata: dict[str, Any], channel: str) -> dict[str, Any]:
    scoped = dict(metadata)
    scoped["channels"] = [channel]
    errors, warnings = validate_materialized(repo, str(metadata.get("project") or project.name), scoped)
    config = load_config(repo)
    result: dict[str, Any] = {
        "selected": channel in selected_channels(metadata),
        "artifact_ready": not errors,
        "blockers": list(errors),
        "warnings": list(warnings),
    }
    if channel == "blog":
        result.update({"adapter": "repository-workflow", "verified_status": "materialized"})
        return result
    if channel == "wechat":
        executable = resolve_executable(str(config.get("md2wechat_executable") or "md2wechat"))
        cover = metadata.get("wechat_cover_image") if isinstance(metadata.get("wechat_cover_image"), dict) else {}
        cover_path = resolve_project_image(repo, project, str(cover.get("local") or ""))
        if not executable:
            result["blockers"].append("未找到 md2wechat；只能使用已登录浏览器手工保存草稿")
        if not cover_path or not cover_path.is_file():
            result["blockers"].append("缺少微信公众号本地封面文件；API 草稿写入需要本地封面")
        result.update(
            {
                "adapter": "md2wechat" if executable else "browser-assisted",
                "adapter_path": executable,
                "artifact_status": "materialized",
                "delivery_capability": "draft_saved" if executable else "manual_required",
                "delivery_mode": "existing-html-direct" if executable else "browser-assisted",
                "ready": not result["blockers"],
            }
        )
        return result
    skills_dir = external_directory(repo, str(config.get("xiaohongshu_skills_dir") or ""))
    script = skills_dir / "scripts" / "publish_pipeline.py" if skills_dir else None
    if not script or not script.is_file():
        result["warnings"].append("未配置 XiaohongshuSkills；可改用已登录浏览器逐轮填充")
    result.update(
        {
            "adapter": "xiaohongshu-skills-preview" if script and script.is_file() else "browser-assisted",
            "adapter_path": str(script) if script and script.is_file() else None,
            "artifact_status": "materialized",
            "delivery_capability": "filled_for_review",
            "server_draft_guaranteed": False,
            "risk": "CDP 自动化可能触发平台风控；先用测试号并人工复核",
            "ready": not result["blockers"],
        }
    )
    return result


def apply_wechat_probe(target: dict[str, Any], payload: Any, returncode: int) -> None:
    """Interpret md2wechat doctor readiness instead of trusting its zero exit code."""
    if returncode or not isinstance(payload, dict) or payload.get("success") is False:
        target["ready"] = False
        target["blockers"].append("md2wechat doctor 执行失败")
        return
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    readiness = data.get("readiness") if isinstance(data.get("readiness"), dict) else {}
    draft_ready = readiness.get("draft") is True
    format_ready = readiness.get("format_api") is True
    target["draft_api_ready"] = draft_ready
    target["format_api_ready"] = format_ready
    if not draft_ready:
        target["ready"] = False
        target["blockers"].append("md2wechat 缺少微信公众号草稿凭据或草稿 API 配置")
    elif not format_ready:
        target["warnings"].append(
            "md2wechat 转换 API 未配置；send-draft 将复用已物化的 article.html 直投草稿，不重新生成正文"
        )


def command_inspect(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    draft_errors, draft_warnings = validate_draft(project, metadata)
    targets = {
        channel: target_readiness(repo, project, metadata, channel)
        for channel in CHANNELS
        if channel in selected_channels(metadata)
    }
    payload: dict[str, Any] = {
        "project": args.project,
        "current_stage": state.get("current_stage", "initialized"),
        "quality": content_metrics(project, metadata),
        "draft": {"ready": not draft_errors, "blockers": draft_errors, "warnings": draft_warnings},
        "targets": targets,
        "deliveries": state.get("deliveries", {}),
        "next_actions": delivery_next_actions(metadata, state),
    }
    if args.probe and "wechat" in targets and targets["wechat"].get("adapter_path"):
        command = [str(targets["wechat"]["adapter_path"]), "doctor", "--json"]
        try:
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            returncode = 124
            probe: Any = {"error": "md2wechat doctor timed out"}
        else:
            returncode = result.returncode
            try:
                probe = redact_adapter_payload(json.loads(result.stdout))
            except json.JSONDecodeError:
                probe = {
                    "stdout": redact_adapter_secrets(result.stdout.strip()),
                    "stderr": redact_adapter_secrets(result.stderr.strip()),
                }
        targets["wechat"]["probe"] = {"returncode": returncode, "result": probe}
        apply_wechat_probe(targets["wechat"], probe, returncode)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def record_delivery(
    project: Path,
    state: dict[str, Any],
    *,
    channel: str,
    item: str,
    status: str,
    account: str = "",
    identifier: str = "",
    note: str = "",
) -> dict[str, Any]:
    if channel not in {"wechat", "rednote"}:
        raise SystemExit("发布状态只支持 wechat 或 rednote")
    if status not in DELIVERY_STATUSES:
        raise SystemExit(f"未知发布状态 {status}")
    record = {
        "status": status,
        "at": now_iso(),
        "account": account,
        "identifier": identifier,
        "note": note,
    }
    state.setdefault("deliveries", {}).setdefault(channel, {})[item] = record
    state["updated_at"] = record["at"]
    atomic_json(state_path(project), state)
    append_event(project, {"type": "delivery", "channel": channel, "item": item, **record})
    return record


def command_record_delivery(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    if args.channel not in selected_channels(metadata):
        raise SystemExit(f"项目没有选择 {args.channel} 渠道")
    item = args.round or "article"
    record = record_delivery(
        project,
        state,
        channel=args.channel,
        item=item,
        status=args.status,
        account=args.account or "",
        identifier=args.identifier or "",
        note=args.note or "",
    )
    print(json.dumps({"channel": args.channel, "item": item, **record}, ensure_ascii=False, indent=2))


def markdown_title_and_body(path: Path) -> tuple[str, str, list[str]]:
    markdown = strip_front_matter(path.read_text(encoding="utf-8"))
    match = H1_RE.search(markdown)
    title = match.group(1).strip() if match else ""
    body = (markdown[: match.start()] + markdown[match.end() :]).strip() if match else markdown.strip()
    images = [url for _, url in IMAGE_RE.findall(markdown)]
    return title, body, images


def run_checked(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)
    return result


def is_tcp_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """Return whether an existing browser CDP endpoint is already listening."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def command_send_draft(args: argparse.Namespace) -> None:
    if not args.confirm:
        raise SystemExit("该命令会操作外部平台；确认目标账号后添加 --confirm")
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    if args.channel not in selected_channels(metadata):
        raise SystemExit(f"项目没有选择 {args.channel} 渠道")
    readiness = target_readiness(repo, project, metadata, args.channel)
    if not readiness.get("ready"):
        raise SystemExit("发布前检查未通过：\n- " + "\n- ".join(readiness.get("blockers", [])))
    config = load_config(repo)
    outputs = expected_outputs(repo, args.project)
    if args.channel == "wechat":
        executable = str(readiness["adapter_path"])
        cover = metadata["wechat_cover_image"]
        cover_path = resolve_project_image(repo, project, str(cover.get("local") or ""))
        if not cover_path:
            raise SystemExit("找不到微信公众号本地封面文件")
        account = args.account or str(config.get("wechat_account") or "")
        with tempfile.TemporaryDirectory(prefix="ymp-wechat-") as temp:
            source = Path(temp) / "article.md"
            body = outputs["wechat_markdown"].read_text(encoding="utf-8")
            source.write_text(
                "---\n"
                f"title: {yaml_string(title_for(project, metadata, 'wechat'))}\n"
                f"description: {yaml_string(str(metadata.get('description', '')).strip())}\n"
                "---\n\n" + body,
                encoding="utf-8",
            )
            common = [str(source), "--draft", "--cover", str(cover_path)]
            if account:
                common.extend(["--wechat-account", account])
            run_adapter_json([executable, "inspect", *common, "--json"], cwd=repo)
            doctor = run_adapter_json([executable, "doctor", "--json"], cwd=repo, timeout=30)
            probe_target = {"ready": True, "blockers": [], "warnings": []}
            apply_wechat_probe(probe_target, doctor, 0)
            if not probe_target["ready"]:
                raise SystemExit("发布前检查未通过：\n- " + "\n- ".join(probe_target["blockers"]))

            cover_material = upload_wechat_material(
                executable,
                repo=repo,
                project=project,
                account=account,
                source=str(cover_path),
                local_path=cover_path,
            )
            html = outputs["wechat_html"].read_text(encoding="utf-8")
            content = prepare_wechat_html(
                executable,
                repo=repo,
                project=project,
                metadata=metadata,
                account=account,
                html=html,
            )
            article: dict[str, Any] = {
                "title": title_for(project, metadata, "wechat"),
                "digest": str(metadata.get("description") or "").strip(),
                "content": content,
                "thumb_media_id": cover_material["media_id"],
                "show_cover_pic": 1,
            }
            author = str(metadata.get("author") or "").strip()
            if author:
                article["author"] = author
            draft_file = Path(temp) / "draft.json"
            draft_file.write_text(
                json.dumps({"articles": [article]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = run_adapter_json(
                [executable, "create_draft", str(draft_file), *adapter_account_flags(account), "--json"],
                cwd=repo,
            )
        result_data = result.get("data") if isinstance(result.get("data"), dict) else {}
        media_id = str(result_data.get("media_id") or "").strip()
        if not media_id:
            raise SystemExit("md2wechat 返回成功，但草稿响应缺少 media_id；未记录 draft_saved")
        record_delivery(
            project,
            state,
            channel="wechat",
            item="article",
            status="draft_saved",
            account=account,
            identifier=media_id,
            note="reused materialized article.html and existing images via md2wechat create_draft; no publish action",
        )
        print(
            json.dumps(
                {"channel": "wechat", "status": "draft_saved", "identifier": media_id},
                ensure_ascii=False,
            )
        )
        return

    round_name = args.round or "round1"
    if not re.fullmatch(r"round[1-9]\d*", round_name):
        raise SystemExit("--round 必须是 round1、round2……")
    script = Path(str(readiness.get("adapter_path") or ""))
    if not script.is_file():
        raise SystemExit("小红书 CLI 自动填充需要在配置中设置 xiaohongshu_skills_dir")
    post = outputs["rednote_root"] / round_name / "post.md"
    if not post.is_file():
        raise SystemExit(f"找不到小红书轮次：{post}")
    title, body, images = markdown_title_and_body(post)
    if not title:
        raise SystemExit(f"{post} 缺少一级标题，无法填写发布标题")
    account = args.account or str(config.get("rednote_account") or "")
    with tempfile.TemporaryDirectory(prefix="ymp-rednote-") as temp:
        title_file = Path(temp) / "title.txt"
        content_file = Path(temp) / "content.txt"
        title_file.write_text(title + "\n", encoding="utf-8")
        content_file.write_text(body + "\n", encoding="utf-8")
        host = str(config.get("rednote_cdp_host") or "127.0.0.1").strip()
        port = int(config.get("rednote_cdp_port") or 9222)
        local_host = host.lower() in {"127.0.0.1", "localhost", "::1"}
        allow_browser_launch = bool(config.get("rednote_allow_browser_launch", False))
        if local_host and not allow_browser_launch and not is_tcp_port_open(host, port):
            raise SystemExit(
                "没有发现已开启 CDP 的现有浏览器；为避免静默新开 Chrome，已停止。"
                "请优先使用 Codex 当前浏览器控制能力，或显式配置 rednote_allow_browser_launch=true。"
            )
        command = [
            sys.executable,
            str(script),
            "--preview",
            "--reuse-existing-tab",
            "--title-file",
            str(title_file),
            "--content-file",
            str(content_file),
        ]
        if images:
            command.extend(["--image-urls", *images])
        if account:
            command.extend(["--account", account])
        command.extend(["--host", host, "--port", str(port)])
        run_checked(command, cwd=script.parents[1])
    record_delivery(
        project,
        state,
        channel="rednote",
        item=round_name,
        status="filled_for_review",
        account=account,
        note="XiaohongshuSkills preview mode filled the editor; server draft is not yet verified",
    )
    print(json.dumps({"channel": "rednote", "round": round_name, "status": "filled_for_review"}, ensure_ascii=False))


def print_validation(errors: list[str], warnings: list[str]) -> None:
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("OK: validation passed")


def command_validate(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, _, metadata = load_project(repo, args.project)
    if args.phase == "draft":
        errors, warnings = validate_draft(project, metadata)
    else:
        errors, warnings = validate_materialized(repo, args.project, metadata)
    print_validation(errors, warnings)


def command_materialize(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    errors, warnings = validate_draft(project, metadata)
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors and not args.allow_incomplete:
        print_validation(errors, [])
    if stage_rank(str(state.get("current_stage", "initialized"))) < stage_rank("reviewed") and not args.allow_incomplete:
        raise SystemExit("必须先完成 AI review，并记录 reviewed 检查点后才能分发")
    channels = selected_channels(metadata)
    polished = strip_front_matter((project / "draft" / "polished.md").read_text(encoding="utf-8"))
    plan = load_plan(project)
    title = title_for(project, metadata, "blog")
    description = str(metadata.get("description", "")).strip()
    date_value = metadata.get("date") or dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tags = plan.get("taxonomy", {}).get("topics") or metadata.get("tags") or ["未分类"]
    categories = plan.get("taxonomy", {}).get("categories") or metadata.get("categories") or ["技术随笔"]
    front_matter = [
        "---",
        f"title: {yaml_string(title)}",
        f"date: {date_value}",
        "tags:",
        *[f"  - {yaml_string(str(value))}" for value in tags],
        "categories:",
        *[f"  - {yaml_string(str(value))}" for value in categories],
        f"description: {yaml_string(description)}",
        "---",
        "",
    ]
    outputs = expected_outputs(repo, args.project)
    if "blog" in channels and metadata.get("publishing_contract_version") == 1 and not english_enabled(project, metadata) and outputs["blog_en"].exists():
        raise SystemExit("已跳过英文版，但最终目录存在旧英文稿；先明确处理旧稿，再分发")
    if "blog" in channels:
        outputs["blog"].parent.mkdir(parents=True, exist_ok=True)
        outputs["blog"].write_text("\n".join(front_matter) + polished.rstrip() + "\n", encoding="utf-8")
        if english_enabled(project, metadata):
            english = plan["english"]
            english_header = list(front_matter)
            english_header[1] = f"title: {yaml_string(english['title'])}"
            english_header[-3] = f"description: {yaml_string(english['description'])}"
            english_header[-2:-2] = ["lang: en", f"translation_of: {yaml_string(args.project)}"]
            translated = strip_front_matter((project/"draft/english.md").read_text())
            outputs["blog_en"].parent.mkdir(parents=True, exist_ok=True)
            outputs["blog_en"].write_text("\n".join(english_header) + translated.rstrip() + "\n")

    if "wechat" in channels:
        wechat_source = strip_front_matter((project / "draft" / "wechat.md").read_text(encoding="utf-8"))
        wechat_html = (project / "draft" / "wechat.html").read_text(encoding="utf-8")
        outputs["wechat_markdown"].parent.mkdir(parents=True, exist_ok=True)
        outputs["wechat_markdown"].write_text(wechat_source.rstrip() + "\n", encoding="utf-8")
        outputs["wechat_html"].write_text(wechat_html.rstrip() + "\n", encoding="utf-8")
    if "rednote" in channels:
        source_rounds = sorted((project / "draft" / "rednote").glob("round*/post.md"), key=lambda p: rednote_round_number(p) or 0)
        for source in source_rounds:
            destination_dir = outputs["rednote_root"] / source.parent.name
            destination_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination_dir / "post.md")
            cards = source.parent / "cards.json"
            if cards.is_file():
                shutil.copy2(cards, destination_dir / "cards.json")
        series_plan = project / "draft" / "rednote" / "series-plan.json"
        if series_plan.is_file():
            outputs["rednote_root"].mkdir(parents=True, exist_ok=True)
            shutil.copy2(series_plan, outputs["rednote_root"] / "series-plan.json")
    output_records: dict[str, Any] = {}
    artifact_keys = []
    if "blog" in channels:
        artifact_keys.append("blog")
        if english_enabled(project, metadata): artifact_keys.append("blog_en")
    if "wechat" in channels:
        artifact_keys.extend(("wechat_markdown", "wechat_html"))
    for key in artifact_keys:
        path = outputs[key]
        output_records[key] = {"path": str(path), "sha256": file_digest(path)}
    if "rednote" in channels:
        output_records["rednote"] = [
            {"path": str(path), "sha256": file_digest(path)}
            for path in sorted(outputs["rednote_root"].glob("round*/*"))
            if path.name in {"post.md", "cards.json"}
        ]
    state["outputs"] = output_records
    update_stage(project, state, "persisted", "materialized blog, WeChat, and RedNote artifacts")
    print(json.dumps(output_records, ensure_ascii=False, indent=2))


def command_publishing_context(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, _, _ = load_project(repo, args.project)
    result = catalog_context(repo)
    source = project / "draft/polished.md"
    result["source_sha256"] = file_digest(source) if source.is_file() else None
    result["plan_path"] = str(project / "draft/publishing-plan.json")
    result["references"] = reference_context(repo, args.project)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="可恢复的语雀多平台内容流水线")
    subparsers = parser.add_subparsers(dest="command", required=True)

    context = subparsers.add_parser("publishing-context", help="读取当前分类话题目录及稿件指纹，供 AI 做发布决策")
    context.add_argument("--project", required=True)
    context.set_defaults(handler=command_publishing_context)

    setup = subparsers.add_parser("setup", help="初始化工作区本地配置")
    setup.add_argument("--posts-dir")
    setup.add_argument("--content-projects-dir")
    setup.add_argument("--wechat-dir")
    setup.add_argument("--rednote-dir")
    setup.add_argument("--image-provider", choices=("imgur", "smms", "github", "chevereto"))
    setup.add_argument("--cover-ratio", choices=("21:9", "23:9"))
    setup.add_argument("--wechat-cover-ratio", choices=("2.35:1",))
    setup.add_argument("--lead-image-style", choices=("ghibli-inspired",))
    setup.add_argument("--wechat-similarity-min", type=float)
    setup.add_argument("--rednote-images-min", type=int, choices=range(1, 10))
    setup.add_argument("--rednote-images-max", type=int, choices=range(1, 10))
    setup.add_argument("--md2wechat-executable")
    setup.add_argument("--wechat-account")
    setup.add_argument("--xiaohongshu-skills-dir")
    setup.add_argument("--rednote-account")
    setup.add_argument("--rednote-cdp-host")
    setup.add_argument("--rednote-cdp-port", type=int)
    setup.add_argument(
        "--rednote-allow-browser-launch",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="允许小红书 CLI 在找不到现有 CDP 浏览器时新开 Chrome（默认禁止）",
    )
    setup.set_defaults(handler=command_setup)

    init = subparsers.add_parser("init", help="创建内容项目")
    init.add_argument("--project", required=True)
    init.add_argument("--yuque-url", required=True)
    init.add_argument("--title")
    init.add_argument("--edit-mode", choices=EDIT_MODES, default="polish-expand")
    init.add_argument("--channels", nargs="+", choices=CHANNELS, default=list(CHANNELS))
    init.set_defaults(handler=command_init)

    resume = subparsers.add_parser("resume", help="显示断点和下一阶段")
    resume.add_argument("--project", required=True)
    resume.set_defaults(handler=command_resume)

    checkpoint = subparsers.add_parser("checkpoint", help="记录阶段检查点")
    checkpoint.add_argument("--project", required=True)
    checkpoint.add_argument("--stage", required=True, choices=CONTENT_STAGES)
    checkpoint.add_argument("--artifact")
    checkpoint.add_argument("--note")
    checkpoint.set_defaults(handler=command_checkpoint)

    fetch = subparsers.add_parser("fetch", help="通过语雀内部接口拉取（兼容回退模式）")
    fetch.add_argument("--project", required=True)
    fetch.add_argument("--login", action="store_true")
    fetch.add_argument("--no-images", action="store_true")
    fetch.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    fetch.set_defaults(handler=command_fetch)

    ingest = subparsers.add_parser("ingest", help="接收 Browser Controller 导出的语雀 Markdown")
    ingest.add_argument("--project", required=True)
    ingest.add_argument("--input", required=True)
    ingest.add_argument("--title")
    ingest.add_argument("--migrate-images", action="store_true")
    ingest.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    ingest.set_defaults(handler=command_ingest)

    upload = subparsers.add_parser("upload-image", help="上传并记录项目图片")
    upload.add_argument("--project", required=True)
    upload.add_argument("--kind", required=True, choices=("cover", "wechat-cover", "section", "rednote"))
    upload.add_argument("--key", required=True)
    upload.add_argument("--file", required=True)
    upload.add_argument("--style")
    upload.add_argument("--language", choices=("zh", "en"), default="zh")
    upload.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    upload.set_defaults(handler=command_upload_image)

    validate = subparsers.add_parser("validate", help="校验草稿或落盘产物")
    validate.add_argument("--project", required=True)
    validate.add_argument("--phase", choices=("draft", "materialized"), default="draft")
    validate.set_defaults(handler=command_validate)

    inspect = subparsers.add_parser("inspect", help="输出内容质量、渠道产物和发布适配器就绪状态")
    inspect.add_argument("--project", required=True)
    inspect.add_argument("--probe", action="store_true", help="调用已安装的公众号适配器执行只读 doctor")
    inspect.set_defaults(handler=command_inspect)

    materialize = subparsers.add_parser("materialize", help="生成三平台最终文件")
    materialize.add_argument("--project", required=True)
    materialize.add_argument("--allow-incomplete", action="store_true")
    materialize.set_defaults(handler=command_materialize)

    send_draft = subparsers.add_parser("send-draft", help="写入公众号草稿，或安全填充小红书编辑器")
    send_draft.add_argument("--project", required=True)
    send_draft.add_argument("--channel", required=True, choices=("wechat", "rednote"))
    send_draft.add_argument("--round", help="小红书轮次，例如 round1")
    send_draft.add_argument("--account", help="外部适配器中的账号别名")
    send_draft.add_argument("--confirm", action="store_true", help="确认操作目标平台账号")
    send_draft.set_defaults(handler=command_send_draft)

    delivery = subparsers.add_parser("record-delivery", help="记录各平台独立的草稿或发布结果")
    delivery.add_argument("--project", required=True)
    delivery.add_argument("--channel", required=True, choices=("wechat", "rednote"))
    delivery.add_argument("--round", help="小红书轮次，例如 round1")
    delivery.add_argument("--status", required=True, choices=DELIVERY_STATUSES)
    delivery.add_argument("--account")
    delivery.add_argument("--identifier")
    delivery.add_argument("--note")
    delivery.set_defaults(handler=command_record_delivery)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
