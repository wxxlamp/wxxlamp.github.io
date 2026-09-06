#!/usr/bin/env python3
"""Find local article candidates; relevance and actual publication need AI review."""
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

import yaml
from workspace import find_workspace_root, load_config, posts_dir
from reference_links import reference_context, resolve_reference, references, post_route


def read_post(path):
    text = path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?', text, re.S)
    metadata = yaml.safe_load(match[1]) if match else {}
    return metadata if isinstance(metadata, dict) else {}, text[match.end():] if match else text


def candidates(repo, queries, exclude='', language='zh', limit=8):
    repo = repo.resolve()
    config = load_config(repo)
    hexo_path = repo/'_config.yml'
    hexo = yaml.safe_load(hexo_path.read_text()) if hexo_path.exists() else {}
    hexo = hexo if isinstance(hexo, dict) else {}
    context = reference_context(repo, exclude)
    origin = context['site_url']
    terms = list(dict.fromkeys(t.strip() for query in queries for t in query.split() if t.strip()))
    records = []
    for path in posts_dir(repo, config).glob('*.md'):
        if path.stem == exclude:
            continue
        meta, body = read_post(path)
        if meta.get('published') is False or meta.get('draft') or meta.get('password'):
            continue
        try:
            if dt.date.fromisoformat(str(meta.get('date',''))[:10]) > dt.date.today():
                continue
        except ValueError:
            continue
        route = post_route(path, meta, hexo)
        if not origin.startswith(('http://','https://')) or not route:
            continue  # Never fabricate a public URL without a supported route.
        title = str(meta.get('title') or path.stem)
        description = str(meta.get('description') or '')
        tags = json.dumps([meta.get('tags',[]),meta.get('categories',[])],ensure_ascii=False)
        from editorial_quality import without_fences
        prose = without_fences(body)
        prose = re.sub(r'!\[[^\]]*\]\([^)]*\)|https?://\S+', '', prose)
        headings = ' '.join(re.findall(r'^#{1,6}\s+(.+)$',prose,re.M))
        score, hits = 0, []
        for term in terms:
            pattern = re.compile(r'(?<![a-z0-9_])'+re.escape(term)+r'(?![a-z0-9_])' if re.fullmatch('[a-zA-Z0-9_]+',term) else re.escape(term),re.I)
            weight = sum(weight for value,weight in ((title,8),(description,5),(tags,3),(headings,3),(prose,1)) if pattern.search(value))
            if weight:
                score += weight
                hits.append(term)
        if not score:
            continue
        url = origin + quote(route, safe='/%')
        target, state = resolve_reference(url,language,context)
        # A Chinese original is not presented as an English translation.
        if language == 'en' and state != 'matched':
            continue
        if language == 'en' and '/en/' not in urlsplit(target).path:
            continue
        match = next((re.search(re.escape(term),prose,re.I) for term in hits if re.search(re.escape(term),prose,re.I)),None)
        snippet = prose[max(0,match.start()-60):match.end()+150] if match else description
        records.append({'source_path':str(path.relative_to(repo)), 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'title':title,'url':target,'language':language,'matched_terms':hits,'score':score,
                        'snippet':snippet.strip(),'publication_status':'needs-live-verification'})
    records.sort(key=lambda row:(-row['score'],row['source_path']))
    return {'queries':terms,'candidates':records[:limit],
            'note':'仅为本地相关候选；AI 阅读命中段落、核对线上页面身份及适用范围后才能引用。没有相关项就记录未选，不凑链接。'}


def validate_related(project, repo, metadata, channels):
    if metadata.get('related_posts_contract_version') != 1 or not {'blog','wechat'} & channels:
        return []
    path=project/'draft/related-posts.json'
    try:
        plan=json.loads(path.read_text())
    except (OSError,ValueError):
        return ['缺少 draft/related-posts.json 历史文章检索记录']
    if not isinstance(plan,dict):
        return ['related-posts.json 必须为对象']
    errors=[]
    raw=project/'raw/source.md'
    if not raw.is_file() or plan.get('source_sha256') != hashlib.sha256(raw.read_bytes()).hexdigest():
        errors.append('历史文章检索记录与当前原稿不一致，请重新检查相关主题')
    if not isinstance(plan.get('queries'),list) or not plan['queries'] or not all(isinstance(x,str) and x.strip() for x in plan['queries']):
        errors.append('历史文章检索需记录实际 queries')
    if not str(plan.get('review_note','')).strip():
        errors.append('历史文章检索需说明取舍，未选入时也说明原因')
    selected=plan.get('selected')
    if not isinstance(selected,list):
        return errors+['历史文章 selected 必须为数组，无相关项时填写空数组']
    context=reference_context(repo,metadata.get('project') or project.name)
    seen=set()
    for item in selected:
        if not isinstance(item,dict):
            errors.append('selected 每项必须为对象');continue
        url=item.get('url','')
        if not isinstance(url,str) or not url.startswith(('http://','https://')):
            errors.append('相关阅读需要完整实际 URL');continue
        if url in seen:
            errors.append('相关阅读 URL 重复')
        seen.add(url)
        source=(repo/str(item.get('source_path',''))).resolve()
        if not source.is_relative_to(posts_dir(repo).resolve()) or not source.is_file():
            errors.append('相关阅读 source_path 必须为历史文章');continue
        if item.get('source_sha256') != hashlib.sha256(source.read_bytes()).hexdigest():
            errors.append('相关阅读源文件已变化，请复核关联与链接')
        meta,_=read_post(source)
        if source.stem == (metadata.get('project') or project.name) or meta.get('published') is False or meta.get('draft') or meta.get('password'):
            errors.append('不能推荐自身、草稿或受保护文章')
        hexo_file = repo/'_config.yml'
        hexo = yaml.safe_load(hexo_file.read_text()) if hexo_file.is_file() else {}
        route = post_route(source, meta, hexo or {})
        target,state=resolve_reference(url,'zh',context)
        from reference_links import normalized_path
        if route != normalized_path(urlsplit(target).path):
            errors.append('相关阅读 URL 与 source_path 对应文章不一致')
        try:
            if dt.date.fromisoformat(str(meta.get('date',''))[:10]) > dt.date.today():
                errors.append('不能推荐未来日期的待发布文章')
        except ValueError:
            errors.append('历史文章日期无法确认')
        if state!='matched' or target!=url:
            errors.append('相关阅读 URL 不是已识别的中文历史路由')
        check=item.get('publication_check',{})
        if not isinstance(check,dict) or check.get('status')!='verified' or check.get('url')!=url or not check.get('checked_at') or not check.get('evidence'):
            errors.append('相关阅读需要实际线上核验：URL、日期、页面身份与内容证据')
        for field in ('relevance','placement','label'):
            if not isinstance(item.get(field),str) or not item[field].strip():
                errors.append('相关阅读缺少 '+field)
        for name in ['polished.md']+(['wechat.md'] if 'wechat' in channels else []):
            draft=project/'draft'/name
            if draft.is_file() and url not in {u for u,_ in references(draft.read_text())}:
                errors.append(f'{name} 遗漏选定的相关阅读：{url}')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query',nargs='+',required=True)
    parser.add_argument('--exclude',default='')
    parser.add_argument('--language',choices=['zh','en'],default='zh')
    parser.add_argument('--limit',type=int,choices=range(1,21),default=8)
    args=parser.parse_args()
    print(json.dumps(candidates(find_workspace_root(),args.query,args.exclude,args.language,args.limit),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
