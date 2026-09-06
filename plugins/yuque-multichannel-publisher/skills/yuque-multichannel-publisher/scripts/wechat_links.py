"""Project external anchors to numbered, copyable references without changing prose."""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit

MARKER = 'data-ymp-links="endnotes"'


def external_web_link(url):
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    # Only article URLs qualify, never substring checks such as mp.weixin.qq.com.evil.
    return not (parsed.scheme == 'https' and parsed.hostname == 'mp.weixin.qq.com'
                and (parsed.path == '/s' or parsed.path.startswith('/s/')))


def link_label_issues(markdown):
    from reference_links import references
    issues = []
    for url, label in references(markdown):
        label = label.strip()
        if url.startswith(('http://', 'https://')) and (
            not label or label.startswith(('http://', 'https://'))
            or label in {'这里', '点击这里', '点击查看', '链接', 'here', 'click here'}
        ):
            issues.append(f'请把链接文字改成文章名、文档主题或具体用途：{url}')
    from markdown_it import MarkdownIt
    import re
    for block in MarkdownIt('commonmark').enable('table').parse(markdown):
        inside_link = False
        for token in block.children or []:
            if token.type == 'link_open': inside_link = True
            elif token.type == 'link_close': inside_link = False
            elif token.type == 'text' and not inside_link:
                for match in re.finditer(r'https?://[^\s<>]+', token.content):
                    issues.append('请把正文裸网址改成有明确名称的 Markdown 链接：' + match[0])
    return list(dict.fromkeys(issues))


def project_links(html, accent='#505967'):
    """Same semantic projection is used to render and to verify the exact result."""
    class Projector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts, self.notes, self.numbers = [], [], {}
            self.anchor = None
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'a' and external_web_link(attrs.get('href', '')):
                url = attrs['href']
                number = self.numbers.setdefault(url, len(self.numbers) + 1)
                self.anchor = {'url': url, 'number': number, 'label': []}
                self.parts.append(f'<span style="color:{accent};font-weight:500;">')
            else:
                if tag == 'img' and self.anchor is not None:
                    self.anchor['label'].append(attrs.get('alt', ''))
                self.parts.append('<' + tag + ''.join(f' {k}="{escape(v or "", quote=True)}"' for k,v in attrs.items()) + '>')
        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
        def handle_data(self, data):
            self.parts.append(escape(data))
            if self.anchor is not None:
                self.anchor['label'].append(data)
        def handle_endtag(self, tag):
            if tag == 'a' and self.anchor is not None:
                item = self.anchor
                label = ''.join(item['label']).strip() or urlsplit(item['url']).hostname
                if not any(note['url'] == item['url'] for note in self.notes):
                    self.notes.append({'url': item['url'], 'label': label, 'number': item['number']})
                self.parts.append(f'</span><sup style="font-size:11px;color:{accent};line-height:0;">[{item["number"]}]</sup>')
                self.anchor = None
            else:
                self.parts.append('</' + tag + '>')
        def handle_comment(self, data):
            self.parts.append('<!--'+data+'-->')
    parser = Projector()
    parser.feed(html)
    result = ''.join(parser.parts)
    if parser.notes:
        result += '<section style="margin:36px 0 0;padding:20px 0 0;border-top:1px solid #e2e2e2;">'
        result += f'<p style="font-size:17px;font-weight:600;color:#242424;margin:0 0 10px;">引用链接</p>'
        result += '<p style="font-size:13px;line-height:1.7;color:#666666;margin:0 0 18px;">以下为网页地址，可复制到浏览器查看。</p>'
        for note in parser.notes:
            result += (f'<p style="margin:0 0 6px;font-size:14px;line-height:1.7;color:#444444;">'
                       f'[{note["number"]}] {escape(note["label"])}</p>'
                       '<p style="margin:0 0 18px;font-size:12px;line-height:1.7;color:#666666;overflow-wrap:anywhere;word-break:break-all;">'
                       + escape(note['url']) + '</p>')
        result += '</section>'
    return f'<section {MARKER}>' + result + '</section>'
