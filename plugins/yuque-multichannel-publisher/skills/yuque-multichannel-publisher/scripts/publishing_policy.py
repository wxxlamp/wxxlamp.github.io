"""Validate AI publication decisions; do not infer quality or translate content."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from markdown_it import MarkdownIt
from editorial_quality import digest, load_object, without_fences
from workspace import load_config, configured_path, posts_dir
from reference_links import reference_context, validate_reference_language, translation_reference_errors


def load_plan(project):
    return load_object(project / 'draft/publishing-plan.json')


def catalog_context(repo):
    config = load_config(repo)
    path = configured_path(repo, config, 'taxonomy_catalog')
    if path.is_file():
        catalog = json.loads(path.read_text())
    else:
        # Portable fallback reads metadata only; English drafts never define taxonomy.
        import yaml
        categories, topics = set(), set()
        for post in posts_dir(repo, config).glob('*.md'):
            text = post.read_text()
            match = re.match(r'^---\s*\n(.*?)\n---', text, re.S)
            if not match:
                continue
            meta = yaml.safe_load(match[1]) or {}
            for key, target in [('categories', categories), ('tags', topics)]:
                values = meta.get(key, [])
                if isinstance(values, str): values = [values]
                target.update(str(x) for x in values)
        catalog = {'categories': [{'zh': x} for x in sorted(categories)], 'topics': [{'zh': x} for x in sorted(topics)]}
    fingerprint = hashlib.sha256(json.dumps(catalog, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {'catalog': catalog, 'catalog_sha256': fingerprint, 'catalog_path': str(path)}


def title_for(project, metadata, channel):
    titles = load_plan(project).get('titles', {})
    value = titles.get(channel, {}) if isinstance(titles, dict) else {}
    return str(value.get('text') or metadata.get('title') or '').strip() if isinstance(value, dict) else ''


def english_enabled(project, metadata):
    english = load_plan(project).get('english', {})
    return 'blog' in (metadata.get('channels') or ['blog', 'wechat', 'rednote']) and isinstance(english, dict) and english.get('decision') == 'generate'


def body_structure(text):
    parser = MarkdownIt('commonmark', {'html': True}).enable('table')
    tokens = parser.parse(text)
    code, headings, images, links = [], [], [], []
    for token in tokens:
        if token.type in ('fence', 'code_block'): code.append((token.info, token.content))
        if token.type == 'heading_open': headings.append(token.tag)
        for child in token.children or []:
            if child.type == 'image': images.append(child.attrGet('src'))
            if child.type == 'link_open': links.append(child.attrGet('href'))
        if token.type in ('html_block', 'inline'):
            images += re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)', token.content, re.I)
    return code, headings, images, links


def validate_plan(project, metadata, repo):
    if metadata.get('publishing_contract_version') != 1:
        return []
    plan = load_plan(project)
    if not plan: return ['缺少 draft/publishing-plan.json；先完成标题、分类话题和英文版决策']
    errors = []
    if plan.get('version') != 1: errors.append('publishing-plan.json version 必须为 1')
    polished = project / 'draft/polished.md'
    if not polished.is_file() or plan.get('source_sha256') != digest(polished):
        errors.append('发布计划与当前 polished.md 不一致，请重新审阅标题、分类和英文决策')
    channels = set(metadata.get('channels') or ['blog', 'wechat', 'rednote'])
    titles = plan.get('titles', {})
    if not isinstance(titles, dict): return errors + ['titles 必须是对象']
    for channel in channels & {'blog', 'wechat'}:
        item = titles.get(channel, {})
        if not isinstance(item, dict) or not item.get('text') or not item.get('reason'):
            errors.append(f'{channel} 需要独立标题 text 与选择理由 reason')
            continue
        text = str(item['text'])
        if '\n' in text or len(text) > (90 if channel == 'blog' else 64): errors.append(f'{channel} 标题过长或包含换行')
        if channel == 'blog' and re.search(r'震惊|必看|必读|速看|保姆级|不看后悔|[!！]{2}|【.*?】', text):
            errors.append('博客标题含营销式表达，请改为明确的对象、问题或方法')
    if 'rednote' in channels:
        rounds = titles.get('rednote', {})
        if not isinstance(rounds, dict): rounds = {}
        for path in (project/'draft/rednote').glob('round*/post.md'):
            item = rounds.get(path.parent.name, {})
            match = re.search(r'^#\s+(.+)$', without_fences(path.read_text()), re.M)
            if not isinstance(item, dict) or not item.get('reason') or not match or item.get('text') != match[1]:
                errors.append(f'{path.parent.name} 缺少与实际笔记一致的独立标题及选择理由')
    if 'blog' not in channels: return errors
    citations = reference_context(repo, metadata.get("project") or project.name)
    if metadata.get('reference_contract_version') == 1:
        if plan.get('references_sha256') != citations['sha256']:
            errors.append('引用目录已变化或未读取；重新执行 publishing-context 并复审引用')
        review = plan.get('references_review', {})
        if not isinstance(review, dict): review = {}
        if not review.get('zh'): errors.append('缺少中文引用语言与来源的实际复审说明')
        errors.extend(validate_reference_language(polished.read_text() if polished.is_file() else '', 'zh', citations))
    taxonomy = plan.get('taxonomy', {})
    if not isinstance(taxonomy, dict): taxonomy = {}
    try: context = catalog_context(repo)
    except (OSError, ValueError, TypeError) as exc: return errors + [f'无法读取分类话题目录：{exc}']
    if taxonomy.get('catalog_sha256') != context['catalog_sha256']: errors.append('分类话题目录已变化或未读取，重新执行 publishing-context')
    if not taxonomy.get('reason'): errors.append('taxonomy 缺少按正文核心内容归类的理由')
    for key, catalog_key, low, high in [('categories','categories',1,1), ('topics','topics',1,3)]:
        values = taxonomy.get(key, [])
        allowed = {x['zh'] for x in context['catalog'].get(catalog_key, [])}
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values) or not low <= len(values) <= high or len(set(values)) != len(values):
            errors.append(f'{key} 需要 {low}–{high} 个不重复的规范名称')
        elif not set(values) <= allowed: errors.append(f'{key} 必须使用当前博客目录中的中文名称，不另造同义或英文标签')
    english = plan.get('english', {})
    if not isinstance(english, dict): english = {}
    if english.get('decision') not in ('generate', 'skip') or not english.get('reason'):
        return errors + ['英文版必须由 AI 明确决策 generate / skip，并说明专业价值与读者收益']
    target = project/'draft/english.md'
    if english['decision'] == 'skip':
        if target.exists(): errors.append('英文版已跳过但遗留 english.md；先明确处理旧稿，不得误发布')
        return errors
    for field in ('audience', 'title', 'description'):
        if not english.get(field): errors.append(f'英文版缺少 {field}')
    if not target.is_file(): return errors + ['需要英文版，但缺少 draft/english.md']
    source = polished.read_text() if polished.is_file() else ''
    text = target.read_text()
    a, b = body_structure(source), body_structure(text)
    if a[0] != b[0]: errors.append('英文版代码块与中文原稿不一致')
    if a[1] != b[1]: errors.append('英文版章节层级或顺序不完整')
    errors.extend(translation_reference_errors(source, text, citations, plan))
    if metadata.get('reference_contract_version') == 1:
        if not review.get('en'): errors.append('缺少英文引用语言、来源等价性与锚点的实际复审说明')
        errors.extend(validate_reference_language(text, 'en', citations))
    prose = re.sub(r'`[^`]*`|https?://\S+', '', without_fences(text))
    if len(re.findall(r'[\u4e00-\u9fff]', prose)) > 40: errors.append('英文版仍有未翻译的中文正文或图注')
    if len(prose) < len(without_fences(source)) * .75: errors.append('英文版疑似遗漏正文；应完整翻译而非摘要')
    records = english.get('images', [])
    if not isinstance(records, list): records = []
    mapped = {}
    for record in records:
        if not isinstance(record, dict): errors.append('英文图片记录必须为对象'); continue
        old, new = record.get('source_url'), record.get('url')
        if old in mapped: errors.append('英文图片重复映射同一原图')
        mapped[old] = new
        if not isinstance(new, str) or not new.startswith('https://'): errors.append('英文图片需要公开 HTTPS URL')
        if record.get('language') not in ('en', 'no-text') or record.get('review_status') != 'passed' or not record.get('review_note'):
            errors.append('每张英文图片都必须实际检查文字语言与语义并记录 review')
        if record.get('language') == 'en' and old == new: errors.append('带文字的中文原图必须生成独立英文版；不能只改 alt')
    if set(mapped) != set(a[2]): errors.append('英文图片清单必须覆盖全部中文正文图片，包括 HTML 图片')
    if set(b[2]) != set(mapped.values()): errors.append('英文正文图片与已审阅的英文图片清单不一致')
    return errors
