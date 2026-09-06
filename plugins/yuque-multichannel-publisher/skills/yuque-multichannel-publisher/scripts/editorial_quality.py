"""Check evidence and freshness of AI reviews, never claim to judge truth or voice."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def without_fences(text):
    # Keep line positions, including fenced code with Markdown-looking headings.
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            lines.append('')
        elif marker:
            fence = marker[1]
            lines.append('')
        else:
            lines.append(line)
    return '\n'.join(lines)


class Content(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.images, self.links = [], [], []
        self.codes, self.current_code = [], None
    def handle_data(self, data):
        self.text.append(data)
        if self.current_code is not None:
            self.current_code.append(data)
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'code':
            self.current_code = []
        if tag == 'img':
            self.images.append(values.get('src', ''))
        if tag == 'a':
            self.links.append(values.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'code' and self.current_code is not None:
            self.codes.append(''.join(self.current_code))
            self.current_code = None


def html_content(html):
    result = Content()
    result.feed(html)
    return result


def validate_html_fidelity(markdown, html):
    from markdown_it import MarkdownIt
    source = html_content(MarkdownIt('commonmark', {'html': True}).enable('table').render(markdown))
    target = html_content(html)
    errors = []
    compact = lambda parts: re.sub(r'\s+', '', ''.join(parts))
    if compact(source.text) != compact(target.text):
        errors.append('微信 HTML 与 Markdown 可见文本不一致（含数字、标点与代码）；请重新排版')
    if source.codes != target.codes:
        errors.append('微信 HTML 代码字符或缩进与 Markdown 不一致')
    if Counter(source.images) != Counter(target.images):
        errors.append('微信 HTML 图片与 Markdown 不一致')
    if Counter(source.links) != Counter(target.links):
        errors.append('微信 HTML 链接与 Markdown 不一致')
    return errors


def load_object(path):
    try:
        result = json.loads(path.read_text())
        return result if isinstance(result, dict) else {}
    except (OSError, ValueError):
        return {}


def validate_series_evidence(plan, polished):
    errors = []
    units = plan.get('content_units', [])
    if not isinstance(units, list) or not units:
        return ['series-plan.json 缺少 content_units 内容材料清单']
    ids = set()
    excluded = set()
    for unit in units:
        if not isinstance(unit, dict):
            errors.append('content_units 每项必须是对象')
            continue
        key = unit.get('id')
        if not isinstance(key, str) or not key or key in ids:
            errors.append('content_units.id 必须非空且唯一')
            continue
        ids.add(key)
        excerpt = unit.get('source_excerpt')
        if not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in polished:
            errors.append(f'{key} 的 source_excerpt 必须可在 polished.md 中定位')
        if unit.get('excluded_reason'):
            excluded.add(key)
    assigned = set()
    unique_sets = set()
    rounds = plan.get('rounds', [])
    if not isinstance(rounds, list):
        return errors + ['rounds 必须是数组']
    for item in rounds:
        if not isinstance(item, dict):
            errors.append('rounds 每项必须是对象')
            continue
        name = item.get('round', '?')
        refs = item.get('unit_ids', [])
        if not isinstance(refs, list) or not refs or not all(isinstance(x, str) for x in refs):
            errors.append(f'{name} 缺少 unit_ids 材料映射')
            continue
        ref_set = frozenset(refs)
        if not ref_set <= ids:
            errors.append(f'{name} 引用了不存在的内容材料')
        if ref_set in unique_sets:
            errors.append(f'{name} 与另一轮使用完全相同的材料；应合并或提供独立材料')
        unique_sets.add(ref_set)
        assigned.update(ref_set)
        for field in ('standalone_test', 'split_reason', 'overlap_review'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f'{name} 缺少 {field}')
    if ids - assigned - excluded:
        errors.append('存在未分配且未说明舍弃原因的内容材料：' + ', '.join(sorted(ids-assigned-excluded)))
    return errors


def required_artifacts(project, channels):
    paths = ['raw/source.md', 'draft/polished.md']
    if 'wechat' in channels:
        paths += ['draft/wechat.md', 'draft/wechat.html']
    if 'rednote' in channels:
        paths += ['draft/rednote/series-plan.json']
        for p in sorted((project/'draft/rednote').glob('round*/post.md')):
            paths += [p.relative_to(project).as_posix(), (p.parent/'cards.json').relative_to(project).as_posix()]
    if (project/'draft/publishing-plan.json').is_file():
        paths.append('draft/publishing-plan.json')
        english = load_object(project/'draft/publishing-plan.json').get('english', {})
        if 'blog' in channels and isinstance(english, dict) and english.get('decision') == 'generate':
            paths.append('draft/english.md')
    return paths


def validate_editorial(project, metadata, channels):
    report = load_object(project/'draft/editorial-review.json')
    if report.get('status') != 'passed':
        return ['缺少通过的 draft/editorial-review.json；需逐平台实际审阅后记录']
    errors = []
    artifacts = report.get('artifacts', {})
    if not isinstance(artifacts, dict):
        artifacts = {}
    for name in required_artifacts(project, channels):
        path = project/name
        if not path.is_file() or artifacts.get(name) != digest(path):
            errors.append(f'编辑复审过期或缺少文件指纹：{name}')
    from workspace import find_workspace_root, state_dir
    voice = state_dir(find_workspace_root(project))/'style-profiles/author-voice.md'
    if voice.is_file():
        if report.get('voice_sha256') != digest(voice):
            errors.append('作者语气档案已变化或缺少 voice_sha256，请按当前档案复审')
    elif report.get('voice_mode') != 'cold-start' or not report.get('voice_limitation'):
        errors.append('缺少作者档案；明确记录 cold-start 和 voice_limitation，不能冒称仿写完成')
    reviews = report.get('reviews', {})
    if not isinstance(reviews, dict):
        reviews = {}
    targets = ['polished'] + (['wechat'] if 'wechat' in channels else [])
    if 'rednote' in channels:
        targets += [p.parent.name for p in (project/'draft/rednote').glob('round*/post.md')]
    if 'draft/english.md' in required_artifacts(project, channels):
        targets.append('english')
    for target in targets:
        review = reviews.get(target, {})
        if not isinstance(review, dict):
            review = {}
        for field in ('voice', 'naturalness', 'typos', 'format', 'facts'):
            if not isinstance(review.get(field), str) or not review[field].strip():
                errors.append(f'{target} 缺少具体的 {field} 审阅说明')
    facts = report.get('fact_checks')
    if not isinstance(facts, list):
        errors.append('fact_checks 必须列出核查项；无外部事实时用空数组并填写 fact_scope')
    else:
        for fact in facts:
            if not isinstance(fact, dict):
                errors.append('fact_checks 项必须是对象')
                continue
            status = fact.get('status')
            if status not in ('verified', 'corrected', 'qualified', 'removed', 'author-account'):
                errors.append('事实核查仍有待确认项，先订正、限定或删除再通过复审')
            for field in ('claim', 'location', 'basis'):
                if not isinstance(fact.get(field), str) or not fact[field].strip():
                    errors.append(f'事实核查缺少 {field}')
            if fact.get('time_sensitive') and status in ('verified', 'corrected'):
                if not str(fact.get('source_url', '')).startswith('https://') or not fact.get('checked_at'):
                    errors.append('时效事实需要权威来源 URL 和核查日期')
    if not report.get('fact_scope'):
        errors.append('缺少 fact_scope 核查范围和限制')
    if 'wechat' in channels:
        md, html = project/'draft/wechat.md', project/'draft/wechat.html'
        if md.is_file() and html.is_file():
            errors.extend(validate_html_fidelity(md.read_text(), html.read_text()))
        layout = report.get('wechat_layout', {})
        if not isinstance(layout, dict):
            layout = {}
        if layout.get('status') != 'passed' or not layout.get('notes'):
            errors.append('缺少微信实际视觉复审和说明')
        previews = layout.get('previews', [])
        if not isinstance(previews, list):
            previews = []
        widths = set()
        for preview in previews:
            if not isinstance(preview, dict):
                continue
            path = (project/str(preview.get('path', ''))).resolve()
            if not path.is_relative_to(project.resolve()) or not path.is_file():
                errors.append('微信预览证据文件不存在或不在项目内')
            elif preview.get('sha256') != digest(path):
                errors.append('微信预览证据已变化')
            if preview.get('html_sha256') != artifacts.get('draft/wechat.html'):
                errors.append('微信预览不是当前 HTML 的版本')
            if preview.get('overflow') or preview.get('brokenImages'):
                errors.append('微信预览仍有横向溢出或未加载图片')
            if isinstance(preview.get('width'), int):
                widths.add(preview['width'])
        if not {375, 430} <= widths:
            errors.append('微信排版需要 375px 与 430px 的实际预览记录')
    return errors
