#!/usr/bin/env python3
"""Manage compact AI-authored voice profiles without analyzing writing style."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from workspace import find_workspace_root, posts_dir, state_dir

REQUIRED_STRINGS = (
    "voice",
    "narrative_perspective",
    "sentence_style",
    "paragraph_style",
    "technical_detail",
    "opening",
    "ending",
)
REQUIRED_LISTS = (
    "structure",
    "transitions",
    "preferred_expressions",
    "avoid_expressions",
    "fact_boundaries",
)
MAX_PROFILE_BYTES = 16_000


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def profile_dir(repo: Path) -> Path:
    return state_dir(repo) / "style-profiles"


def index_path(repo: Path) -> Path:
    return profile_dir(repo) / "profile-index.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists() and default is not None:
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"文件不存在：{path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON 无法解析：{path}: {exc}") from None
    if not isinstance(value, dict):
        raise SystemExit(f"JSON 顶层必须是对象：{path}")
    return value


def front_matter(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---", 4)
    if end < 0:
        return []
    return text[4:end].splitlines()


def scalar_value(lines: list[str], key: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1).strip().strip("\"'")
    return ""


def categories_from_front_matter(lines: list[str]) -> list[str]:
    for index, line in enumerate(lines):
        match = re.match(r"^categories?\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        inline = match.group(1).strip()
        if inline:
            if inline.startswith("[") and inline.endswith("]"):
                return [part.strip().strip("\"'") for part in inline[1:-1].split(",") if part.strip()]
            return [inline.strip("\"'")]
        values: list[str] = []
        for following in lines[index + 1 :]:
            item = re.match(r"^\s+-\s+(.+?)\s*$", following)
            if item:
                values.append(item.group(1).strip().strip("\"'"))
                continue
            if following and not following[0].isspace():
                break
        return values
    return []


def article_record(repo: Path, path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = front_matter(text)
    date = scalar_value(lines, "date")
    title = scalar_value(lines, "title") or path.stem
    return {
        "path": path.relative_to(repo).as_posix(),
        "sha256": sha256_file(path),
        "date": date,
        "title": title,
        "categories": categories_from_front_matter(lines),
    }


def category_corpus(repo: Path, category: str) -> list[dict[str, Any]]:
    records = []
    for path in sorted(posts_dir(repo).glob("*.md")):
        record = article_record(repo, path)
        if category == "default" or category in record["categories"]:
            records.append(record)
    records.sort(key=lambda item: (item["date"], item["path"]), reverse=True)
    return records


def corpus_fingerprint(records: list[dict[str, Any]]) -> str:
    compact = [{"path": item["path"], "sha256": item["sha256"]} for item in sorted(records, key=lambda x: x["path"])]
    raw = json.dumps(compact, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def profile_filename(category: str) -> str:
    suffix = hashlib.sha256(category.encode("utf-8")).hexdigest()[:12]
    return f"style-{suffix}.json"


def load_index(repo: Path) -> dict[str, Any]:
    return load_json(index_path(repo), {"schema_version": 1, "profiles": {}})


def profile_entry(repo: Path, category: str) -> tuple[dict[str, Any], Path | None]:
    index = load_index(repo)
    entry = index.get("profiles", {}).get(category)
    if not isinstance(entry, dict) or not entry.get("file"):
        return {}, None
    path = profile_dir(repo) / str(entry["file"])
    return entry, path


def changed_paths(old_records: list[dict[str, Any]], new_records: list[dict[str, Any]]) -> list[str]:
    old = {item["path"]: item["sha256"] for item in old_records}
    new = {item["path"]: item["sha256"] for item in new_records}
    paths = {path for path in old.keys() | new.keys() if old.get(path) != new.get(path)}
    return sorted(paths)


def prepare_payload(repo: Path, category: str, limit: int) -> dict[str, Any]:
    corpus = category_corpus(repo, category)
    if not corpus:
        return {
            "action": "blocked",
            "category": category,
            "reason": "该分类没有可用文章",
            "profile_path": None,
            "read_samples": [],
        }
    fingerprint = corpus_fingerprint(corpus)
    entry, path = profile_entry(repo, category)
    if path and path.is_file():
        profile = load_json(path)
        if entry.get("corpus_fingerprint") == fingerprint:
            return {
                "action": "reuse",
                "category": category,
                "profile_path": str(path),
                "reason": "缓存命中；只读取 profile_path，不读取样本文章",
                "read_samples": [],
                "corpus_fingerprint": fingerprint,
            }
        changed = changed_paths(entry.get("source_corpus", []), corpus)
        changed_existing = [item["path"] for item in corpus if item["path"] in changed]
        anchors = [item["path"] for item in corpus if item["path"] not in changed][:2]
        samples = (changed_existing + anchors)[:limit]
        return {
            "action": "refresh",
            "category": category,
            "profile_path": str(path),
            "reason": "语料指纹变化；读取旧档案、变化文章和最多两篇锚点文章",
            "changed_paths": changed,
            "read_samples": samples,
            "corpus_fingerprint": fingerprint,
        }
    return {
        "action": "learn",
        "category": category,
        "profile_path": str(profile_dir(repo) / profile_filename(category)),
        "reason": "首次建立该分类语气档案",
        "read_samples": [item["path"] for item in corpus[:limit]],
        "corpus_fingerprint": fingerprint,
    }


def validate_profile_draft(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_STRINGS:
        value = profile.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} 必须是非空字符串")
    for field in REQUIRED_LISTS:
        value = profile.get(field)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{field} 必须是非空字符串数组")
    examples = profile.get("micro_examples", [])
    if not isinstance(examples, list) or not all(isinstance(item, str) for item in examples):
        errors.append("micro_examples 必须是字符串数组")
    elif len(examples) > 5 or any(len(item) > 120 for item in examples):
        errors.append("micro_examples 最多 5 条，每条不超过 120 字")
    forbidden = {"articles", "full_text", "source_content", "raw_samples"}
    present = sorted(forbidden & profile.keys())
    if present:
        errors.append(f"不得缓存样本全文字段：{', '.join(present)}")
    return errors


def resolve_samples(repo: Path, category: str, raw_samples: list[str], corpus: list[dict[str, Any]]) -> list[str]:
    valid = {item["path"] for item in corpus}
    resolved: list[str] = []
    for raw in raw_samples:
        path = Path(raw)
        if path.is_absolute():
            try:
                normalized = path.resolve().relative_to(repo).as_posix()
            except ValueError:
                raise SystemExit(f"样本必须位于仓库中：{path}") from None
        else:
            normalized = path.as_posix()
        if normalized not in valid:
            raise SystemExit(f"样本不属于分类“{category}”或不在 source/_posts：{normalized}")
        if normalized not in resolved:
            resolved.append(normalized)
    minimum = min(3, len(corpus))
    if len(resolved) < minimum or len(resolved) > 8:
        raise SystemExit(f"样本数量必须为 {minimum}–8，当前为 {len(resolved)}")
    return resolved


def command_prepare(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    print(json.dumps(prepare_payload(repo, args.category, args.limit), ensure_ascii=False, indent=2))


def command_save(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    corpus = category_corpus(repo, args.category)
    if not corpus:
        raise SystemExit(f"分类“{args.category}”没有样本文章")
    draft = load_json(Path(args.input))
    errors = validate_profile_draft(draft)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    samples = resolve_samples(repo, args.category, args.samples, corpus)
    profile = {key: value for key, value in draft.items() if key not in {"schema_version", "category"}}
    profile.update(
        {
            "schema_version": 1,
            "category": args.category,
            "updated_at": now_iso(),
            "sample_paths": samples,
        }
    )
    encoded = json.dumps(profile, ensure_ascii=False, indent=2).encode("utf-8")
    if len(encoded) > MAX_PROFILE_BYTES:
        raise SystemExit(f"语气档案为 {len(encoded)} bytes，超过 {MAX_PROFILE_BYTES} bytes；请继续提炼")
    filename = profile_filename(args.category)
    destination = profile_dir(repo) / filename
    atomic_json(destination, profile)
    index = load_index(repo)
    index.setdefault("profiles", {})[args.category] = {
        "file": filename,
        "updated_at": profile["updated_at"],
        "corpus_fingerprint": corpus_fingerprint(corpus),
        "source_corpus": [
            {"path": item["path"], "sha256": item["sha256"]}
            for item in sorted(corpus, key=lambda value: value["path"])
        ],
        "sample_paths": samples,
    }
    index["schema_version"] = 1
    atomic_json(index_path(repo), index)
    print(destination)


def command_list(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    index = load_index(repo)
    result = []
    for category, entry in sorted(index.get("profiles", {}).items()):
        path = profile_dir(repo) / entry["file"]
        result.append(
            {
                "category": category,
                "path": str(path),
                "exists": path.is_file(),
                "updated_at": entry.get("updated_at"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_validate(args: argparse.Namespace) -> None:
    repo = find_workspace_root()
    index = load_index(repo)
    errors: list[str] = []
    for category, entry in index.get("profiles", {}).items():
        path = profile_dir(repo) / str(entry.get("file", ""))
        if not path.is_file():
            errors.append(f"{category}: 缓存文件不存在：{path}")
            continue
        profile = load_json(path)
        errors.extend(f"{category}: {error}" for error in validate_profile_draft(profile))
        if profile.get("category") != category:
            errors.append(f"{category}: profile.category 不匹配")
        if path.stat().st_size > MAX_PROFILE_BYTES:
            errors.append(f"{category}: 文件超过 {MAX_PROFILE_BYTES} bytes")
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print(f"OK: {len(index.get('profiles', {}))} style profile(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理由 AI 编写的紧凑语气档案")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="判断复用、首次学习或增量刷新")
    prepare.add_argument("--category", required=True)
    prepare.add_argument("--limit", type=int, choices=range(3, 9), default=6)
    prepare.set_defaults(handler=command_prepare)

    save = subparsers.add_parser("save", help="校验并保存 AI 生成的语气档案")
    save.add_argument("--category", required=True)
    save.add_argument("--input", required=True)
    save.add_argument("--samples", nargs="+", required=True)
    save.set_defaults(handler=command_save)

    listing = subparsers.add_parser("list", help="列出缓存档案")
    listing.set_defaults(handler=command_list)

    validate = subparsers.add_parser("validate", help="校验全部缓存档案")
    validate.set_defaults(handler=command_validate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
