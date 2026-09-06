#!/usr/bin/env python3
"""Render author-approved Markdown into portable inline HTML without rewriting."""
import argparse
from pathlib import Path
from markdown_it import MarkdownIt


def render(markdown, theme='ink'):
    accent = {'ink': '#315c53', 'warm': '#8a5036'}[theme]
    styles = {
        'paragraph_open': 'margin:0 0 20px;line-height:1.85;',
        'blockquote_open': f'margin:24px 0;padding:12px 16px;border-left:3px solid {accent};background:#f5f7f6;color:#515854;',
        'bullet_list_open': 'padding-left:24px;margin:16px 0 24px;',
        'ordered_list_open': 'padding-left:28px;margin:16px 0 24px;',
        'list_item_open': 'margin:8px 0;line-height:1.85;',
        'strong_open': f'font-weight:600;color:{accent};',
        'link_open': f'color:{accent};text-decoration:underline;overflow-wrap:anywhere;',
        'table_open': 'border-collapse:collapse;width:100%;font-size:14px;line-height:1.7;',
        'th_open': 'padding:10px 8px;border:1px solid #dfe5e2;background:#f2f5f3;text-align:left;',
        'td_open': 'padding:10px 8px;border:1px solid #dfe5e2;text-align:left;overflow-wrap:anywhere;',
        'hr': 'border:0;border-top:1px solid #e1e7e3;margin:32px 0;',
        'image': 'display:block;max-width:100%;height:auto;margin:24px auto;border-radius:4px;',
        'code_inline': 'font-size:14px;font-family:Menlo,Consolas,monospace;background:#f2f4f3;padding:2px 4px;border-radius:3px;overflow-wrap:anywhere;',
    }
    md = MarkdownIt('commonmark', {'html': False}).enable('table')
    # Raw HTML cannot be silently stripped/escaped in a publishing artifact.
    raw_tokens = MarkdownIt('commonmark', {'html':True}).parse(markdown)
    if any(token.type in ('html_block', 'html_inline') or any(c.type == 'html_inline' for c in (token.children or [])) for token in raw_tokens):
        raise ValueError('请先把原始 HTML 转成等义 Markdown，或由 AI 保真排版并验证')
    def decorate(tokens):
        for token in tokens:
            if token.type in styles:
                token.attrSet('style', styles[token.type])
            if token.type == 'heading_open':
                level = int(token.tag[1])
                size = {1:22, 2:19, 3:17}.get(level,16)
                token.attrSet('style', f'font-size:{size}px;line-height:1.45;font-weight:600;color:{accent};margin:32px 0 16px;text-align:left;')
            if token.children:
                if any(c.type=='html_inline' for c in token.children):
                    raise ValueError('行内 HTML 请先转为等义 Markdown')
                decorate(token.children)
    tokens = md.parse(markdown)
    decorate(tokens)
    old_fence = md.renderer.rules['fence']
    def fence(tokens, idx, options, env):
        result = old_fence(tokens, idx, options, env)
        return result.replace('<pre>', '<pre style="margin:24px 0;padding:16px;background:#f4f6f5;color:#263630;border-radius:6px;font-size:13px;line-height:1.7;white-space:pre-wrap;overflow-wrap:anywhere;">').replace('<code', '<code style="font-family:Menlo,Consolas,monospace;"', 1)
    md.renderer.rules['fence'] = fence
    # Indented code receives the same wrapping style as fenced code.
    old_code = md.renderer.rules['code_block']
    def code_block(tokens, idx, options, env):
        return old_code(tokens, idx, options, env).replace('<pre>', '<pre style="white-space:pre-wrap;overflow-wrap:anywhere;padding:16px;background:#f4f6f5;font-size:13px;line-height:1.7;">')
    md.renderer.rules['code_block'] = code_block
    body = md.renderer.render(tokens, md.options, {})
    return '<section style="box-sizing:border-box;width:100%;max-width:680px;margin:0 auto;padding:8px 16px 28px;background:#fff;color:#333;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.85;letter-spacing:0.2px;text-align:left;overflow-wrap:anywhere;">' + body + '</section>\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--theme', choices=['ink','warm'], default='ink')
    args=parser.parse_args()
    source=Path(args.input).read_text()
    result=render(source,args.theme)
    from editorial_quality import validate_html_fidelity
    errors=validate_html_fidelity(source,result)
    if errors:
        raise SystemExit('\n'.join(errors))
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(result)
    print(args.output)

if __name__=='__main__':
    main()
