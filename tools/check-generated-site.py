"""Validate generated bilingual routes and reader-compatible feeds after hexo generate."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET
import re

root = Path(__file__).resolve().parents[1] / 'public'
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonical, self.alternates, self.headings = [], [], {}, []
        self.lang = None
        self.feed_links = []
        self.google_ui = False
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if 'translation-tools' in a.get('class', '').split(): self.google_ui = True
        if re.fullmatch(r'h[1-6]', tag) and a.get('id'): self.headings.append(a['id'])
        if tag == 'link':
            if a.get('rel') == 'canonical': self.canonical.append(a['href'])
            if a.get('hreflang'): self.alternates[a['hreflang']] = a['href']
            if a.get('type') in ['application/atom+xml', 'application/rss+xml']: self.feed_links.append(a['href'])

files = [file for file in root.rglob('*.html') if file.relative_to(root).parts[0] != 'design-history']
broken = []
for file in files:
    page = Page(file.read_text())
    assert not page.google_ui, f'Obsolete Google translation UI: {file}'
    assert len(page.feed_links) == 2, (file, page.feed_links)
    expected_prefix = '/en/' if page.lang == 'en' and not str(file).endswith('resume-en/index.html') else '/'
    # English resume uses the same English subscription feeds as the English site.
    if str(file).endswith('resume-en/index.html'): expected_prefix = '/en/'
    assert set(page.feed_links) == {expected_prefix + 'atom.xml', expected_prefix + 'rss.xml'}, (file, page.feed_links)
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.netloc:
            if parsed.hostname not in {'wxxlamp.cn', 'www.wxxlamp.cn', 'wxxlamp.github.io', 'www.wxxlamp.github.io'}: continue
        elif not link.startswith('/'): continue
        target = root / unquote(parsed.path).lstrip('/')
        if not target.suffix: target /= 'index.html'
        if not target.exists(): broken.append((str(file.relative_to(root)), link))
assert not broken, f'Missing internal links: {broken[:15]}'

posts = [p for p in root.rglob('*.html') if re.fullmatch(r'\d{4}/\d{2}/\d{2}/[^/]+/index.html', str(p.relative_to(root)))]
paired = 0
selected = {p.stem for p in (root.parent / 'source/_posts/en').glob('*.md')}
for original in posts:
    english = root / 'en' / original.relative_to(root)
    if original.parent.name not in selected:
        assert not english.exists(), f'Unselected English article: {english}'
        assert 'en' not in Page(original.read_text()).alternates
        continue
    assert english.exists(), f'Missing selected English article: {original}'
    paired += 1
    zh, en = Page(original.read_text()), Page(english.read_text())
    assert en.lang == 'en'
    # Old raw-HTML Markdown may swallow a source heading. Every existing source
    # anchor must remain present and ordered in the translated page.
    assert zh.headings == [h for h in en.headings if h in zh.headings], f'Section anchor mismatch: {english}'
    assert len(en.canonical) == 1 and '/en/' in en.canonical[0]
    assert en.alternates['zh-CN'] == zh.canonical[0]
    assert zh.alternates['en'] == en.canonical[0]
assert paired == len(selected), (paired, len(selected))

ns = {'a':'http://www.w3.org/2005/Atom', 'content':'http://purl.org/rss/1.0/modules/content/'}
for prefix in ['', 'en/']:
    atom = ET.parse(root / (prefix + 'atom.xml')).getroot()
    rss = ET.parse(root / (prefix + 'rss.xml')).getroot()
    entries, items = atom.findall('a:entry', ns), rss.findall('channel/item')
    assert len(entries) == len(items) == 20
    ids = [e.findtext('a:id', namespaces=ns) for e in entries]
    assert len(ids) == len(set(ids))
    for e in entries:
        content = e.find('a:content', ns)
        assert content is not None and content.attrib.get('type') == 'html'
        assert content.text and len(content.text) > 100
        url = e.findtext('a:id', namespaces=ns)
        assert url.startswith('https://wxxlamp.cn/' + prefix)
        assert ('/en/' in url) == bool(prefix)
    assert ids == [item.findtext('guid') for item in items]
    for item in items: assert len(item.findtext('content:encoded', namespaces=ns)) > 100
assert (root / 'CNAME').read_text().strip() == 'wxxlamp.cn'
print(f'Validated {len(files)} pages, {paired} selected bilingual article pairs, {len(posts) - paired} Chinese-only articles, four full-content feeds, and all internal paths.')
