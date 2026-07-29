#!/usr/bin/env python3
"""Deterministic state and artifact handling for a resumable content pipeline."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from workspace import DEFAULT_CONFIG, configured_path, config_path, find_workspace_root, load_config, posts_dir

STAGES = [
    "initialized",
    "fetched",
    "polished",
    "illustrated",
    "persisted",
    "reviewed",
    "drafted",
    "published",
]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((https://[^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n?", re.DOTALL)
SCRIPT_DIR = Path(__file__).resolve().parent


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
    if path.exists():
        print(path)
        return
    config = dict(DEFAULT_CONFIG)
    for key in ("posts_dir", "content_projects_dir", "wechat_dir", "rednote_dir", "image_provider"):
        value = getattr(args, key)
        if value:
            config[key] = value
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
    metadata = {
        "project": args.project,
        "yuque_url": args.yuque_url,
        "title": args.title or "",
        "description": "",
        "tags": [],
        "categories": [],
        "cover_image": {},
        "section_images": {},
        "rednote_images": {},
        "created_at": created,
    }
    state = {
        "schema_version": 1,
        "project": args.project,
        "repo_root": str(repo),
        "current_stage": "initialized",
        "created_at": created,
        "updated_at": created,
        "checkpoints": [{"stage": "initialized", "at": created, "note": "project created"}],
        "outputs": {},
    }
    atomic_json(metadata_path(project), metadata)
    atomic_json(state_path(project), state)
    append_event(project, {"type": "initialized", "yuque_url": args.yuque_url})
    print(project)


def command_resume(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    current = state.get("current_stage", "initialized")
    index = stage_rank(current)
    next_stage = STAGES[index + 1] if index + 1 < len(STAGES) else "complete"
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


def require_image_ratio(path: Path, kind: str) -> tuple[int, int] | None:
    dimensions = image_dimensions(path)
    expected = {"cover": 23 / 9, "section": 16 / 9}.get(kind)
    if expected is None:
        return dimensions
    if dimensions is None:
        raise SystemExit(f"无法读取 {path.suffix} 图片尺寸；封面和章节图请使用 PNG/JPEG")
    width, height = dimensions
    actual = width / height
    if abs(actual - expected) / expected > 0.01:
        label = "23:9" if kind == "cover" else "16:9"
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
    dimensions = require_image_ratio(image, args.kind)
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
    if args.kind == "cover":
        record["ratio"] = "23:9"
        metadata["cover_image"] = record
    elif args.kind == "section":
        record["ratio"] = "16:9"
        metadata.setdefault("section_images", {})[args.key] = record
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


def validate_draft(project: Path, metadata: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    polished_path = project / "draft" / "polished.md"
    if not polished_path.is_file():
        return [f"缺少 {polished_path}"], warnings
    polished = strip_front_matter(polished_path.read_text(encoding="utf-8"))
    for field in ("title", "description"):
        if not str(metadata.get(field, "")).strip():
            errors.append(f"metadata.json 缺少 {field}")
    cover_url = metadata.get("cover_image", {}).get("url", "")
    if not cover_url:
        errors.append("metadata.json 缺少 cover_image.url")
    elif cover_url not in "\n".join(polished.splitlines()[:20]):
        errors.append("封面 URL 必须出现在 polished.md 开头 20 行内")
    if metadata.get("cover_image", {}).get("ratio") != "23:9":
        errors.append("metadata.json 的 cover_image.ratio 必须为 23:9")
    headings = H1_RE.findall(polished)
    if not headings:
        warnings.append("正文没有一级标题，无法验证章节配图")
    lines = polished.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if not match:
            continue
        following = [value.strip() for value in lines[index + 1 :] if value.strip()][:3]
        if not any(IMAGE_RE.fullmatch(value) for value in following):
            errors.append(f"一级标题“{match.group(1)}”后 3 个非空行内缺少 HTTPS 图片")
        section_record = metadata.get("section_images", {}).get(match.group(1), {})
        if section_record.get("ratio") != "16:9":
            errors.append(f"metadata.json 缺少一级标题“{match.group(1)}”的 16:9 section_images 记录")
    wechat = project / "draft" / "wechat.md"
    if not wechat.is_file():
        errors.append(f"缺少 {wechat}")
    wechat_html = project / "draft" / "wechat.html"
    if not wechat_html.is_file():
        errors.append(f"缺少 AI 排版产物 {wechat_html}")
    rounds = sorted((project / "draft" / "rednote").glob("round*/post.md"))
    if not rounds:
        errors.append("至少需要一个 draft/rednote/roundN/post.md")
    for round_path in rounds:
        text = strip_front_matter(round_path.read_text(encoding="utf-8"))
        visible = re.sub(r"[#*`>\[\]()!https:/._-]", "", text)
        if len(visible) > 1200:
            warnings.append(f"{round_path.parent.name} 可见字符约 {len(visible)}，建议压缩到 900 以内")
        if not IMAGE_RE.search(text):
            errors.append(f"{round_path.parent.name} 缺少 HTTPS 配图")
        if not re.search(r"(?m)^#[^#]", text):
            warnings.append(f"{round_path.parent.name} 建议用一级标题作为发布标题")
    return errors, warnings


def expected_outputs(repo: Path, slug: str) -> dict[str, Path]:
    config = load_config(repo)
    return {
        "blog": posts_dir(repo, config) / f"{slug}.md",
        "wechat_markdown": configured_path(repo, config, "wechat_dir") / slug / "article.md",
        "wechat_html": configured_path(repo, config, "wechat_dir") / slug / "article.html",
        "rednote_root": configured_path(repo, config, "rednote_dir") / slug,
    }


def validate_materialized(repo: Path, slug: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    outputs = expected_outputs(repo, slug)
    for name in ("blog", "wechat_markdown", "wechat_html"):
        if not outputs[name].is_file():
            errors.append(f"缺少 {name}: {outputs[name]}")
    rounds = sorted(outputs["rednote_root"].glob("round*/post.md"))
    if not rounds:
        errors.append(f"缺少小红书轮次：{outputs['rednote_root']}")
    if outputs["blog"].is_file() and not outputs["blog"].read_text(encoding="utf-8").startswith("---\n"):
        errors.append("博客文章缺少 front matter")
    return errors, warnings


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
        errors, warnings = validate_materialized(repo, args.project)
    print_validation(errors, warnings)


def command_materialize(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    project, state, metadata = load_project(repo, args.project)
    errors, warnings = validate_draft(project, metadata)
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors and not args.allow_incomplete:
        print_validation(errors, [])
    polished = strip_front_matter((project / "draft" / "polished.md").read_text(encoding="utf-8"))
    wechat_source = strip_front_matter((project / "draft" / "wechat.md").read_text(encoding="utf-8"))
    wechat_html = (project / "draft" / "wechat.html").read_text(encoding="utf-8")
    title = str(metadata.get("title", "")).strip()
    description = str(metadata.get("description", "")).strip()
    date_value = metadata.get("date") or dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tags = metadata.get("tags") or ["未分类"]
    categories = metadata.get("categories") or ["技术随笔"]
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
    outputs["blog"].parent.mkdir(parents=True, exist_ok=True)
    outputs["blog"].write_text("\n".join(front_matter) + polished.rstrip() + "\n", encoding="utf-8")
    outputs["wechat_markdown"].parent.mkdir(parents=True, exist_ok=True)
    outputs["wechat_markdown"].write_text(wechat_source.rstrip() + "\n", encoding="utf-8")
    outputs["wechat_html"].write_text(wechat_html.rstrip() + "\n", encoding="utf-8")
    source_rounds = sorted((project / "draft" / "rednote").glob("round*/post.md"))
    for source in source_rounds:
        destination = outputs["rednote_root"] / source.parent.name / "post.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    output_records: dict[str, Any] = {}
    for key in ("blog", "wechat_markdown", "wechat_html"):
        path = outputs[key]
        output_records[key] = {"path": str(path), "sha256": file_digest(path)}
    output_records["rednote"] = [
        {"path": str(path), "sha256": file_digest(path)}
        for path in sorted(outputs["rednote_root"].glob("round*/post.md"))
    ]
    state["outputs"] = output_records
    update_stage(project, state, "persisted", "materialized blog, WeChat, and RedNote artifacts")
    print(json.dumps(output_records, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="可恢复的语雀多平台内容流水线")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = subparsers.add_parser("setup", help="初始化工作区本地配置")
    setup.add_argument("--posts-dir")
    setup.add_argument("--content-projects-dir")
    setup.add_argument("--wechat-dir")
    setup.add_argument("--rednote-dir")
    setup.add_argument("--image-provider", choices=("imgur", "smms", "github", "chevereto"))
    setup.set_defaults(handler=command_setup)

    init = subparsers.add_parser("init", help="创建内容项目")
    init.add_argument("--project", required=True)
    init.add_argument("--yuque-url", required=True)
    init.add_argument("--title")
    init.set_defaults(handler=command_init)

    resume = subparsers.add_parser("resume", help="显示断点和下一阶段")
    resume.add_argument("--project", required=True)
    resume.set_defaults(handler=command_resume)

    checkpoint = subparsers.add_parser("checkpoint", help="记录阶段检查点")
    checkpoint.add_argument("--project", required=True)
    checkpoint.add_argument("--stage", required=True, choices=STAGES)
    checkpoint.add_argument("--artifact")
    checkpoint.add_argument("--note")
    checkpoint.set_defaults(handler=command_checkpoint)

    fetch = subparsers.add_parser("fetch", help="调用现有 skill 拉取语雀文档")
    fetch.add_argument("--project", required=True)
    fetch.add_argument("--login", action="store_true")
    fetch.add_argument("--no-images", action="store_true")
    fetch.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    fetch.set_defaults(handler=command_fetch)

    upload = subparsers.add_parser("upload-image", help="上传并记录项目图片")
    upload.add_argument("--project", required=True)
    upload.add_argument("--kind", required=True, choices=("cover", "section", "rednote"))
    upload.add_argument("--key", required=True)
    upload.add_argument("--file", required=True)
    upload.add_argument("--provider", choices=("imgur", "smms", "github", "chevereto"))
    upload.set_defaults(handler=command_upload_image)

    validate = subparsers.add_parser("validate", help="校验草稿或落盘产物")
    validate.add_argument("--project", required=True)
    validate.add_argument("--phase", choices=("draft", "materialized"), default="draft")
    validate.set_defaults(handler=command_validate)

    materialize = subparsers.add_parser("materialize", help="生成三平台最终文件")
    materialize.add_argument("--project", required=True)
    materialize.add_argument("--allow-incomplete", action="store_true")
    materialize.set_defaults(handler=command_materialize)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
