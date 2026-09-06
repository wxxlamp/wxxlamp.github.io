#!/usr/bin/env python3
"""Render author-approved Markdown into portable inline HTML without rewriting."""
import argparse
from pathlib import Path
from markdown_it import MarkdownIt
from wechat_links import project_links, link_label_issues


# The agent selects article_type from the whole article, not keyword counts.
THEMES = {
    'neutral': '#505967',
    'blue': '#285a91',
    'warm': '#8a5036',
    'sage': '#426657',
    'ink': '#315c53',  # Keep the old explicit theme name usable.
}
ARTICLE_THEMES = {
    'technical': 'blue',
    'essay': 'warm',
    'lifestyle': 'sage',
    'neutral': 'neutral',
}


def resolve_theme(theme='auto', article_type='neutral'):
    if article_type not in ARTICLE_THEMES:
        raise ValueError('未知文章类型：' + article_type)
    selected = ARTICLE_THEMES[article_type] if theme == 'auto' else theme
    if selected not in THEMES:
        raise ValueError('未知主题：' + selected)
    return selected


def render(markdown, theme='auto', link_mode='endnotes', article_type='neutral'):
    if link_mode not in ('endnotes', 'inline'):
        raise ValueError('未知链接呈现模式')
    theme = resolve_theme(theme, article_type)
    accent = THEMES[theme]
    styles = {
        'paragraph_open': 'margin:0 0 20px;line-height:1.85;text-align:left;',
        'blockquote_open': f'margin:24px 0;padding:12px 16px;border-left:3px solid {accent};background:#f6f6f6;color:#505050;',
        'bullet_list_open': 'padding-left:24px;margin:16px 0 24px;',
        'ordered_list_open': 'padding-left:28px;margin:16px 0 24px;',
        'list_item_open': 'margin:8px 0;line-height:1.85;',
        'strong_open': 'font-weight:600;color:#242424;',
        'link_open': f'color:{accent};text-decoration:underline;overflow-wrap:anywhere;',
        'table_open': 'border-collapse:collapse;width:100%;margin:20px 0 24px;font-size:14px;line-height:1.7;',
        'th_open': 'padding:10px 8px;border:1px solid #e2e2e2;background:#f5f5f5;text-align:left;',
        'td_open': 'padding:10px 8px;border:1px solid #e2e2e2;text-align:left;overflow-wrap:anywhere;',
        'hr': 'border:0;border-top:1px solid #e3e3e3;margin:32px 0;',
        'image': 'display:block;max-width:100%;height:auto;margin:24px auto;border-radius:4px;',
        'code_inline': 'font-size:14px;font-family:Menlo,Consolas,monospace;background:#f4f4f4;padding:2px 4px;border-radius:3px;overflow-wrap:anywhere;',
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
                token.attrSet('style', f'font-size:{size}px;line-height:1.45;font-weight:600;color:#242424;margin:36px 0 16px;text-align:left;')
            if token.children:
                if any(c.type=='html_inline' for c in token.children):
                    raise ValueError('行内 HTML 请先转为等义 Markdown')
                decorate(token.children)
    tokens = md.parse(markdown)
    decorate(tokens)
    if tokens and tokens[0].type == 'paragraph_open':
        tokens[0].attrSet('style', 'font-size:17px;line-height:1.85;color:#333333;margin:4px 0 24px;')
    old_fence = md.renderer.rules['fence']
    def fence(tokens, idx, options, env):
        result = old_fence(tokens, idx, options, env)
        return result.replace('<pre>', '<pre style="margin:24px 0;padding:16px;background:#f5f5f5;color:#303030;border-radius:6px;font-size:13px;line-height:1.7;white-space:pre-wrap;overflow-wrap:anywhere;">').replace('<code', '<code style="font-family:Menlo,Consolas,monospace;"', 1)
    md.renderer.rules['fence'] = fence
    # Indented code receives the same wrapping style as fenced code.
    old_code = md.renderer.rules['code_block']
    def code_block(tokens, idx, options, env):
        return old_code(tokens, idx, options, env).replace('<pre>', '<pre style="white-space:pre-wrap;overflow-wrap:anywhere;padding:16px;background:#f5f5f5;font-size:13px;line-height:1.7;">')
    md.renderer.rules['code_block'] = code_block
    body = md.renderer.render(tokens, md.options, {})
    if link_mode == 'endnotes':
        body = project_links(body, accent)
    return f'<section data-ymp-theme="{theme}" data-ymp-article-type="{article_type}" style="box-sizing:border-box;width:100%;max-width:680px;margin:0 auto;padding:8px 16px 28px;background:#fff;color:#333;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.85;letter-spacing:0.2px;text-align:left;overflow-wrap:anywhere;">' + body + '</section>\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--theme', choices=['auto', *THEMES], default='auto', help='显式主题优先；auto 按文章类型选色')
    parser.add_argument('--article-type', choices=list(ARTICLE_THEMES), default='neutral', help='AI 根据文章目的选择；未指定时采用中性灰')
    parser.add_argument('--link-mode', choices=['endnotes','inline'], default='endnotes')
    args=parser.parse_args()
    source=Path(args.input).read_text()
    issues = link_label_issues(source)
    if issues:
        raise SystemExit('\n'.join(issues))
    result=render(source,args.theme,args.link_mode,args.article_type)
    from editorial_quality import validate_html_fidelity
    errors=validate_html_fidelity(source,result)
    if errors:
        raise SystemExit('\n'.join(errors))
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(result)
    print(args.output)

if __name__=='__main__':
    main()
