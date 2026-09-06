"""Resolve real bilingual references; never invent translated pages or verify remote content."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

import yaml
from markdown_it import MarkdownIt
from workspace import load_config, configured_path, posts_dir


def references(text):
    """Markdown, reference-style links, HTML anchors and bare URLs; exclude code/images."""
    result = []
    class Anchors(HTMLParser):
        def __init__(self):
            super().__init__(); self.url = None; self.label = ''
        def handle_starttag(self, tag, attrs):
            if tag == 'a': self.url = dict(attrs).get('href'); self.label = ''
        def handle_data(self, data):
            if self.url: self.label += data
        def handle_endtag(self, tag):
            if tag == 'a' and self.url:
                result.append((self.url, self.label)); self.url = None
    html = Anchors()
    for token in MarkdownIt('commonmark', {'html': True}).enable('table').parse(text):
        if token.type == 'html_block': html.feed(token.content)
        url, label = None, ''
        for child in token.children or []:
            if child.type == 'link_open': url, label = child.attrGet('href'), ''
            elif child.type == 'link_close':
                if url is not None: result.append((url, label))
                url = None
            elif child.type == 'html_inline': html.feed(child.content)
            elif url is not None: label += child.content
            elif child.type == 'text':
                for match in re.finditer(r'https?://[^\s<>"\)\]）]+', child.content):
                    result.append((match[0].rstrip('.,，。'), child.content))
    return result


def normalized_path(path):
    path = unquote(path or '/')
    return path.removesuffix('index.html').rstrip('/') + '/'


def reference_context(repo, current_slug=None):
    config = load_config(repo)
    file = configured_path(repo, config, 'reference_catalog')
    catalog = json.loads(file.read_text()) if file.is_file() else {}
    hexo_file = repo/'_config.yml'
    hexo = yaml.safe_load(hexo_file.read_text()) if hexo_file.is_file() else {}
    origin = str((hexo or {}).get('url') or '').rstrip('/')
    hosts = set(catalog.get('site_aliases', []))
    if origin: hosts.add(urlsplit(origin).netloc)
    routes = {}
    for post in posts_dir(repo, config).glob('*.md'):
        if post.stem == current_slug: continue
        match = re.match(r'^---\s*\n(.*?)\n---', post.read_text(), re.S)
        meta = yaml.safe_load(match[1]) if match else {}
        if not meta or not meta.get('date'): continue
        date = str(meta['date'])[:10].split('-')
        if len(date) != 3: continue
        permalink = str(meta.get('permalink') or (hexo or {}).get('permalink') or ':year/:month/:day/:title/')
        for key, value in zip(('year','month','day','title'), [*date, str(meta.get('slug') or post.stem)]):
            permalink = permalink.replace(':'+key, value)
        if ':' in permalink: continue  # Unsupported layouts are reviewed explicitly, never guessed.
        route = normalized_path('/'+permalink.lstrip('/'))
        variants = {'zh': route}
        english = post.parent/'en'/post.name
        if english.is_file():
            match_en = re.match(r'^---\s*\n(.*?)\n---', english.read_text(), re.S)
            em = yaml.safe_load(match_en[1]) if match_en else {}
            if em and em.get('lang') == 'en' and em.get('translation_of') == post.stem:
                variants['en'] = '/en'+route
        for value in variants.values(): routes[value] = variants
    for old, new in catalog.get('route_aliases', {}).items():
        if normalized_path(new) in routes: routes[normalized_path(old)] = routes[normalized_path(new)]
    result = {'site_url': origin, 'hosts': sorted(hosts), 'routes': routes, 'pairs': catalog.get('pairs', []), 'original_sources': catalog.get('original_sources', [])}
    result['sha256'] = hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return result


def resolve_reference(url, language, context):
    """Return target and state (matched, unavailable, missing, external, local)."""
    parsed = urlsplit(url)
    internal = parsed.netloc in context['hosts'] if parsed.netloc else parsed.path.startswith('/')
    if internal:
        route = normalized_path(parsed.path)
        variants = context['routes'].get(route)
        if variants:
            target = variants.get(language)
            if not target: return url, 'unavailable'
            return urlunsplit((parsed.scheme, parsed.netloc, target, parsed.query, parsed.fragment)), 'matched'
        # Only article paths are asserted here; pages and assets have their own route checks.
        if re.match(r'^/(?:en/)?\d{4}/\d{2}/\d{2}/', route): return url, 'missing'
        return url, 'local'
    for pair in context['pairs']:
        if url in (pair.get('zh'), pair.get('en')):
            return pair.get(language) or url, 'matched'
    for source in context.get('original_sources', []):
        if source.get('url') == url and source.get('language') != language:
            return url, 'unavailable'
    return url, 'external'


def validate_reference_language(text, language, context):
    errors = []
    marker = r'中文原文|in Chinese' if language == 'en' else r'英文原文|in English'
    for url, label in references(text):
        if not url.strip():
            errors.append('引用链接地址为空：'+label)
            continue
        target, state = resolve_reference(url, language, context)
        if state == 'missing': errors.append(f'引用的站内文章不存在：{url}')
        elif state == 'matched' and target != url: errors.append(f'{language} 引用应指向同语言版本：{url} → {target}')
        elif state == 'unavailable' and not re.search(marker, label, re.I):
            errors.append(f'引用没有 {language} 版本，保留原文时须在链接文字标注语言：{url}')
    return errors


def translation_reference_errors(source, english, context, plan):
    target_urls = {u for u, _ in references(english)}
    mappings = plan.get('reference_links', [])
    if not isinstance(mappings, list): return ['reference_links 必须为数组']
    source_urls = {u for u, _ in references(source)}
    reviewed = {}
    errors = []
    for item in mappings:
        if not isinstance(item, dict) or item.get('source_url') not in source_urls or item.get('url') not in target_urls or item.get('review_status') != 'passed' or not item.get('review_note'):
            errors.append('引用替换需记录实际存在的源 URL、英文 URL 及同一内容的复核结果')
            continue
        if resolve_reference(item['source_url'], 'en', context)[1] != 'external':
            errors.append('已知站内/双语引用不得用手工映射绕过真实语言路由')
            continue
        reviewed[item['source_url']] = item['url']
    for url in source_urls:
        expected, _ = resolve_reference(url, 'en', context)
        expected = reviewed.get(url, expected)
        if expected not in target_urls: errors.append(f'英文版遗漏原文引用链接或其已核验译版：{url}')
    return errors
