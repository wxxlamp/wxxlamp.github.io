#!/usr/bin/env python3
"""
Markdown Image Migrator - 迁移 Markdown 中的远程图片到图床

用法:
    python3 md-image-migrator.py <markdown_file> [--provider imgur|smms|github]
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
IMG_UPLOADER = SCRIPT_DIR.parent / "img-uploader" / "image-uploader.py"


def extract_image_urls(content: str) -> list:
    """提取 Markdown 中的所有图片 URL"""
    # 匹配 ![](url) 和 ![alt](url) 格式
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)

    urls = []
    for alt, url in matches:
        # 跳过本地路径和 data URI
        if url.startswith('http://') or url.startswith('https://'):
            urls.append((alt, url))

    return urls


def download_image(url: str, temp_dir: Path) -> Path:
    """下载图片到临时目录"""
    try:
        # 生成临时文件名
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix
        if not ext or ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']:
            ext = '.png'  # 默认扩展名

        filename = f"{uuid.uuid4().hex[:8]}{ext}"
        local_path = temp_dir / filename

        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            f.write(response.content)

        return local_path
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return None


def upload_image(local_path: Path, provider: str = "imgur") -> str:
    """使用 img-uploader 上传图片"""
    if not IMG_UPLOADER.exists():
        print(f"  ❌ 找不到 img-uploader: {IMG_UPLOADER}")
        return None

    cmd = ["python3", str(IMG_UPLOADER), str(local_path), "--provider", provider]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"  ❌ 上传失败: {result.stderr}")
            return None

        # 解析输出获取 URL
        output = result.stdout

        # 查找 URL 行
        for line in output.split('\n'):
            if line.startswith('URL:') or line.startswith('CDN URL:'):
                url = line.split(':', 1)[1].strip()
                return url
            # GitHub 格式
            if 'cdn.jsdelivr.net' in line or 'raw.githubusercontent.com' in line:
                if 'URL:' in line:
                    return line.split(':', 1)[1].strip()

        # 如果找不到 URL，打印完整输出用于调试
        print(f"  ⚠️  无法解析上传结果，完整输出:\n{output}")
        return None

    except Exception as e:
        print(f"  ❌ 上传异常: {e}")
        return None


def migrate_markdown_images(md_file: str, provider: str = "imgur", dry_run: bool = False):
    """迁移 Markdown 文件中的图片"""
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"错误: 文件不存在: {md_file}")
        return False

    # 读取文件内容
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取图片 URL
    image_urls = extract_image_urls(content)
    if not image_urls:
        print("没有找到远程图片链接")
        return True

    print(f"找到 {len(image_urls)} 个远程图片链接")
    print("-" * 50)

    if dry_run:
        print("预览模式，不执行实际下载和上传:")
        for alt, url in image_urls:
            print(f"  - {url}")
        return True

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 处理每个图片
        replacements = {}
        for i, (alt, url) in enumerate(image_urls, 1):
            print(f"\n[{i}/{len(image_urls)}] 处理: {url[:60]}...")

            # 下载图片
            local_path = download_image(url, temp_path)
            if not local_path:
                print(f"  ⏭️  跳过此图片")
                continue

            print(f"  ✅ 已下载: {local_path.name}")

            # 上传图片
            new_url = upload_image(local_path, provider)
            if not new_url:
                print(f"  ⏭️  跳过此图片")
                continue

            print(f"  ✅ 已上传: {new_url[:60]}...")
            replacements[url] = new_url

        # 替换 Markdown 内容
        if replacements:
            new_content = content
            for old_url, new_url in replacements.items():
                new_content = new_content.replace(old_url, new_url)

            # 保存文件
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"\n" + "=" * 50)
            print(f"✅ 完成! 已替换 {len(replacements)} 个图片链接")
            print(f"文件已更新: {md_path}")
            return True
        else:
            print(f"\n⚠️  没有成功替换任何图片")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="迁移 Markdown 中的远程图片到图床",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 md-image-migrator.py source/_posts/article.md
    python3 md-image-migrator.py source/_posts/article.md --provider github
    python3 md-image-migrator.py source/_posts/article.md --dry-run  # 预览模式
        """
    )
    parser.add_argument('file', help='Markdown 文件路径')
    parser.add_argument('--provider', default='imgur',
                        choices=['imgur', 'smms', 'github'],
                        help='图床提供商 (默认: imgur)')
    parser.add_argument('--dry-run', action='store_true',
                        help='预览模式，不执行实际下载和上传')

    args = parser.parse_args()

    success = migrate_markdown_images(args.file, args.provider, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
