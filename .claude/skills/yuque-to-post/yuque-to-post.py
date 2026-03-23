#!/usr/bin/env python3
"""
Yuque to Post - 下载语雀文档并转换为 Hexo 博客文章

用法:
    python3 yuque-to-post.py <yuque_url> [--tags tag1,tag2] [--categories cat1,cat2] [--desc description]
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SOURCE_POSTS_DIR = PROJECT_ROOT / "source" / "_posts"
YUQUE_FETCHER = SCRIPT_DIR.parent / "yuque-fetcher" / "yuque-fetcher.py"


def run_yuque_fetcher(url: str, temp_output: str) -> bool:
    """调用 yuque-fetcher 下载文档"""
    if not YUQUE_FETCHER.exists():
        print(f"错误: 找不到 yuque-fetcher: {YUQUE_FETCHER}")
        print("请确保 yuque-fetcher 技能已安装")
        return False

    cmd = ["python3", str(YUQUE_FETCHER), url, "-o", temp_output]
    print(f"执行: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"yuque-fetcher 执行失败:")
            print(result.stderr)
            return False
        print(result.stdout)
        return True
    except subprocess.TimeoutExpired:
        print("下载超时，请重试")
        return False
    except Exception as e:
        print(f"执行失败: {e}")
        return False


def extract_title_from_content(content: str) -> str:
    """从 Markdown 内容中提取标题"""
    # 尝试匹配第一个 # 标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def extract_description_from_content(content: str, max_length: int = 50) -> str:
    """从 Markdown 内容中提取描述（备用方案）"""
    # 移除 Markdown 格式
    text = re.sub(r'!\[.*?\]\(.*?\)', '', content)  # 移除图片
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # 替换链接为文本
    text = re.sub(r'[#*`]', '', text)  # 移除标记符号
    text = re.sub(r'\n+', ' ', text)  # 换行转空格
    text = re.sub(r'\s+', ' ', text)  # 合并空格

    text = text.strip()

    # 取前 max_length 个字符
    if len(text) > max_length:
        return text[:max_length].strip() + "..."
    return text


def generate_front_matter(title: str, tags: list, categories: list, description: str) -> str:
    """生成 Hexo front matter"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")

    # 处理默认值
    if not tags:
        tags = ["未分类"]
    if not categories:
        categories = ["技术随笔"]
    if not description:
        description = f"{title} - 本文档从语雀导入"

    # 转义特殊字符
    title = title.replace('"', '\\"')
    description = description.replace('"', '\\"')

    front_matter = f"""---
title: "{title}"
date: {date_str}
tags:
{chr(10).join(f'   - {tag}' for tag in tags)}
categories:
{chr(10).join(f'   - {cat}' for cat in categories)}
description: "{description}"
---

"""
    return front_matter


def process_markdown(input_file: str, output_file: str, tags: list, categories: list, desc: str = ""):
    """处理 Markdown 文件，添加 front matter"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题
    title = extract_title_from_content(content)
    if not title:
        title = Path(input_file).stem
        print(f"警告: 未能提取标题，使用文件名: {title}")
    else:
        print(f"提取到标题: {title}")

    # 如果没有提供描述，使用简单提取
    if not desc:
        desc = extract_description_from_content(content)
        print(f"自动生成描述: {desc[:50]}...")

    # 生成 front matter
    front_matter = generate_front_matter(title, tags, categories, desc)

    # 移除原文档中的标题（因为 front matter 已包含）
    # 如果内容以 # 标题开头，移除它
    content = re.sub(r'^#\s+.+\n+', '', content)

    # 组合最终内容
    final_content = front_matter + content

    # 确保目标目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    return title


def sanitize_filename(title: str) -> str:
    """将标题转换为安全的文件名"""
    # 移除或替换不安全的字符
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    filename = re.sub(r'\s+', '-', filename)
    filename = filename.strip('-')
    return filename if filename else "untitled"


def git_commit_new_post(file_path: Path, title: str):
    """自动 git add 和 commit 新文章"""
    try:
        # 检查是否在 git 仓库中
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("⚠️  未在 git 仓库中，跳过 commit")
            return False

        # git add
        result = subprocess.run(
            ["git", "add", str(file_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"⚠️  git add 失败: {result.stderr}")
            return False

        # 检查是否有变更要提交
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("⚠️  没有变更需要提交")
            return False

        # git commit
        commit_msg = f"feat(content): 添加文章《{title}》"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"⚠️  git commit 失败: {result.stderr}")
            return False

        print(f"✅ 已自动提交: {commit_msg}")
        return True

    except Exception as e:
        print(f"⚠️  git 操作失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="下载语雀文档并转换为 Hexo 博客文章",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 yuque-to-post.py https://www.yuque.com/user/repo/slug --desc "文章描述" --filename "english-title"
    python3 yuque-to-post.py https://www.yuque.com/user/repo/slug --desc "描述" --filename "my-post" --commit
        """
    )
    parser.add_argument('url', help='语雀文档 URL')
    parser.add_argument('--tags', type=str, help='标签，用逗号分隔 (默认: 未分类)')
    parser.add_argument('--categories', type=str, help='分类，用逗号分隔 (默认: 技术随笔)')
    parser.add_argument('--desc', type=str, help='文章描述 (preview模式之外必需)')
    parser.add_argument('--filename', type=str, help='英文文件名，小写连字符格式 (默认使用标题转义)')
    parser.add_argument('--commit', action='store_true', help='生成后自动 git commit')
    parser.add_argument('--preview', action='store_true', help='仅下载并显示内容预览，不生成文件')

    args = parser.parse_args()

    # 检查非预览模式下 desc 是否必需
    if not args.preview and not args.desc:
        print("错误: 非预览模式下 --desc 参数是必需的")
        print("用法示例:")
        print(f"  python3 {sys.argv[0]} <url> --desc '文章描述'")
        sys.exit(1)

    # 检查 source/_posts 目录
    if not SOURCE_POSTS_DIR.exists():
        print(f"错误: 找不到博客文章目录: {SOURCE_POSTS_DIR}")
        print("请确保在 Hexo 博客项目根目录下运行此脚本")
        sys.exit(1)

    print(f"博客文章目录: {SOURCE_POSTS_DIR}")

    # 创建临时文件路径
    temp_file = f"/tmp/yuque_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"

    # 步骤 1: 下载语雀文档
    print(f"\n[1/2] 正在下载语雀文档: {args.url}")
    if not run_yuque_fetcher(args.url, temp_file):
        sys.exit(1)

    # 检查临时文件是否存在
    if not os.path.exists(temp_file):
        print(f"错误: 下载的文件不存在: {temp_file}")
        sys.exit(1)

    # 如果是预览模式，显示内容并退出
    if args.preview:
        print("\n" + "="*50)
        print("文档内容预览（前 2000 字符）:")
        print("="*50)
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:2000])
            if len(content) > 2000:
                print(f"\n... (共 {len(content)} 字符)")
        print("="*50)
        print(f"\n标题: {extract_title_from_content(content)}")
        os.remove(temp_file)
        sys.exit(0)

    # 步骤 2: 处理标签和分类
    print(f"\n[2/2] 生成博客文章...")
    tags = args.tags.split(',') if args.tags else []
    categories = args.categories.split(',') if args.categories else []

    # 步骤 3: 处理 Markdown 并生成最终文件
    title = process_markdown(temp_file, temp_file, tags, categories, args.desc)

    # 生成目标文件名（优先使用 --filename 参数，否则使用标题）
    if args.filename:
        safe_title = sanitize_filename(args.filename)
        # 确保有 .md 后缀
        if not safe_title.endswith('.md'):
            safe_title = safe_title.rstrip('.')
    else:
        safe_title = sanitize_filename(title)

    output_file = SOURCE_POSTS_DIR / f"{safe_title}.md"

    # 处理文件名冲突
    counter = 1
    original_output = output_file
    while output_file.exists():
        output_file = SOURCE_POSTS_DIR / f"{safe_title}-{counter}.md"
        counter += 1

    if output_file != original_output:
        print(f"注意: 文件 {original_output.name} 已存在，使用 {output_file.name}")

    # 移动文件到目标位置
    os.rename(temp_file, output_file)

    print(f"\n✅ 成功生成博客文章!")
    print(f"   标题: {title}")
    print(f"   路径: {output_file}")

    # 显示文件内容预览
    print(f"\n文件预览:")
    print("-" * 50)
    with open(output_file, 'r', encoding='utf-8') as f:
        preview = f.read()[:500]
        print(preview)
        if len(preview) >= 500:
            print("...")
    print("-" * 50)

    # 自动 commit（如果启用）
    if args.commit:
        git_commit_new_post(output_file, title)


if __name__ == "__main__":
    main()
