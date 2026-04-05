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


def suggest_english_filename(title: str) -> str:
    """根据中文标题内容建议一个简短的英文文件名"""
    import unicodedata

    # 如果已经是英文，则返回标准化版本
    if not any('\u4e00' <= char <= '\u9fff' for char in title):
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '-', filename)
        filename = re.sub(r'[^a-zA-Z0-9\-_.]', '', filename)
        filename = filename.strip('-').lower()
        return filename if filename else "untitled"

    # 对于中文标题，提供一个建议的英文名称
    # 首先定义一些常见的中文到英文的映射
    common_phrases = {
        "我的": "my",
        "的": "",
        "年": "-year",
        "目标": "-goals",
        "达成": "-achievement",
        "情况": "-status",
        "总结": "-summary",
        "回顾": "-retrospective",
        "计划": "-plan",
        "工作": "-work",
        "学习": "-learning",
        "技术": "-tech",
        "分享": "-share",
        "心得": "-insights",
        "经验": "-experience",
        "博客": "-blog",
        "文章": "-post",
        "2025": "2025",
        "2026": "2026",
        "2024": "2024",
        "2023": "2023",
        "2022": "2022",
        "2021": "2021",
        "2020": "2020",
        "上半年": "-first-half",
        "下半年": "-second-half",
        "上半年总结": "-first-half-summary",
        "下半年总结": "-second-half-summary",
        "年终": "-year-end",
        "年初": "-year-start",
        "心得体会": "-reflections",
        "年终总结": "-year-end-summary",
        "年度总结": "-annual-review",
        "个人": "-personal",
        "成长": "-growth",
        "反思": "-reflection",
        "复盘": "-review",
        "感悟": "-thoughts",
        "历程": "-journey",
        "思考": "-thoughts",
        "想法": "-ideas"
    }

    # 对标题进行简单的中文分词替代
    processed_title = title
    for chinese, english in sorted(common_phrases.items(), key=lambda x: len(x[0]), reverse=True):
        processed_title = processed_title.replace(chinese, english)

    # 移除多余空格并使用连字符连接
    filename = re.sub(r'\s+', '-', processed_title)
    filename = re.sub(r'[<>:"/\\|?*,.，。！？【】「」\[\]{}]', '', filename)
    filename = re.sub(r'-+', '-', filename)  # 合并多个连续的连字符
    filename = filename.strip('-').lower()

    # 防止出现多个连续的连字符
    filename = re.sub(r'-+', '-', filename)

    # 如果处理后的结果仍然包含中文或者太复杂，使用通用名称加哈希
    if any('\u4e00' <= char <= '\u9fff' for char in filename) or len(filename) > 50:
        # 创建一个简短的基于内容的标识符
        import hashlib
        hash_suffix = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        return f"blog-post-{hash_suffix}"

    return filename if filename else "untitled"


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
    """将标题转换为安全的文件名，优先使用英文"""
    import unicodedata

    # 检测是否包含中文字符
    if any('\u4e00' <= char <= '\u9fff' for char in title):
        print(f"检测到中文标题: {title}")
        print("提示: 为了更好的SEO和URL可读性，建议使用 --filename 参数指定简短的英文文件名")

        # 对于中文标题，使用原逻辑，但提供更好的提示
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '-', filename)
        filename = filename.strip('-')

        # 如果生成的文件名仍然包含中文字符，建议用户使用英文名
        if any('\u4e00' <= char <= '\u9fff' for char in filename):
            print("警告: 文件名包含中文字符，可能会影响URL可读性")
    else:
        # 对于英文标题的处理
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '-', filename)
        filename = re.sub(r'[^a-zA-Z0-9\-_.]', '', filename)  # 只保留字母、数字、连字符、下划线和点
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
        # 先尝试生成建议的英文文件名
        suggested_name = suggest_english_filename(title)

        # 如果建议的英文名看起来合理，优先使用它
        if suggested_name and suggested_name != "untitled" and not suggested_name.startswith("blog-post-"):
            safe_title = suggested_name
            print(f"使用建议的英文文件名: {suggested_name}")
        else:
            safe_title = sanitize_filename(title)
            # 显示建议但不自动使用
            print(f"建议的英文文件名: {suggested_name}")
            print(f"提示: 如需使用英文文件名，可在命令中添加 --filename '{suggested_name}'")

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
