#!/usr/bin/env python3
"""
自动验证 Hexo 本地站点
- 检查页面可访问性
- 验证关键元素是否存在
- 检查样式加载情况
- 生成验证报告
"""

import subprocess
import time
import sys
import os
import json
from urllib.request import urlopen
from urllib.error import URLError

def check_server(url, max_retries=30, delay=1):
    """等待服务器启动"""
    print(f"⏳ 等待服务器启动: {url}")
    for i in range(max_retries):
        try:
            response = urlopen(url, timeout=5)
            if response.status == 200:
                print(f"✅ 服务器已就绪")
                return True
        except URLError:
            pass
        time.sleep(delay)
        print(f"  重试 {i+1}/{max_retries}...")
    return False

def fetch_page(url):
    """获取页面内容"""
    try:
        response = urlopen(url, timeout=10)
        return response.read().decode('utf-8')
    except Exception as e:
        return f"ERROR: {e}"

def validate_page(url, name, checks):
    """验证页面"""
    print(f"\n🔍 验证 {name}: {url}")
    html = fetch_page(url)

    if html.startswith("ERROR:"):
        return {"status": "FAILED", "error": html}

    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func(html)
        except Exception as e:
            results[check_name] = False

    return {
        "status": "PASSED" if all(results.values()) else "FAILED",
        "checks": results
    }

def check_title(html):
    """检查标题"""
    return "<title>" in html and "</title>" in html

def check_css_loaded(html):
    """检查 CSS 是否加载"""
    return "<link" in html and ".css" in html

def check_js_loaded(html):
    """检查 JS 是否加载"""
    return "<script" in html

def check_content(html):
    """检查内容区域"""
    return len(html) > 1000

def check_navigation(html):
    """检查导航菜单"""
    nav_keywords = ["Archives", "About", "Tags", "Categories"]
    return any(kw in html for kw in nav_keywords)

def check_posts(html):
    """检查文章列表"""
    return "<article" in html or "post" in html.lower()

def check_footer(html):
    """检查页脚"""
    return "footer" in html.lower() or "©" in html

def main():
    base_url = "http://localhost:4000"

    print("=" * 50)
    print("Hexo 本地站点自动验证")
    print("=" * 50)

    # 检查服务器
    if not check_server(base_url):
        print("❌ 服务器启动失败")
        return 1

    results = {}

    # 验证首页
    results["首页"] = validate_page(base_url, "首页", {
        "标题存在": check_title,
        "CSS加载": check_css_loaded,
        "JS加载": check_js_loaded,
        "内容非空": check_content,
        "导航菜单": check_navigation,
        "文章列表": check_posts,
        "页脚存在": check_footer
    })

    # 验证归档页
    results["归档页"] = validate_page(f"{base_url}/archives", "归档页", {
        "标题存在": check_title,
        "CSS加载": check_css_loaded,
        "内容非空": check_content
    })

    # 验证标签页
    results["标签页"] = validate_page(f"{base_url}/tags", "标签页", {
        "标题存在": check_title,
        "CSS加载": check_css_loaded,
        "内容非空": check_content
    })

    # 打印报告
    print("\n" + "=" * 50)
    print("验证报告")
    print("=" * 50)

    all_passed = True
    for page_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        icon = "✅" if status == "PASSED" else "❌"
        print(f"\n{icon} {page_name}: {status}")

        if "checks" in result:
            for check_name, passed in result["checks"].items():
                check_icon = "✓" if passed else "✗"
                print(f"   {check_icon} {check_name}")

        if status == "FAILED":
            all_passed = False
            if "error" in result:
                print(f"   错误: {result['error']}")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有验证通过！")
        return 0
    else:
        print("⚠️  部分验证失败，请检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())
