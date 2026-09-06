"""Audit real same-language references, with optional source-only URL repairs."""
import argparse
import json
import re
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts'))
from reference_links import reference_context, references, resolve_reference, validate_reference_language

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fix',action='store_true')
args=parser.parse_args()
context=reference_context(root)
files=[*sorted((root/'source/_posts').rglob('*.md')),root/'source/about/index.md',root/'source/en/about/index.md']
errors=[]; changes=[]; count=0; internal=0
for file in files:
    lang='en' if 'en' in file.relative_to(root/'source').parts else 'zh'
    text=file.read_text(); body=text.split('---',2)[-1]
    urls=references(body); count+=len(urls)
    mapping={}
    for url,_ in urls:
        target,state=resolve_reference(url,lang,context)
        if state in ('matched','unavailable','missing') and (url.startswith('/') or any(host in url for host in context['hosts'])): internal+=1
        if target!=url: mapping[url]=target
    if args.fix and mapping:
        lines=text.splitlines(keepends=True);fence=None;out=[]
        for line in lines:
            match=re.match(r'^\s*(`{3,}|~{3,})',line)
            if match:
                if fence is None: fence=match[1]
                elif match[1][0]==fence[0] and len(match[1])>=len(fence): fence=None
                out.append(line);continue
            if fence:out.append(line);continue
            parts=re.split(r'(`+[^`]*`+)',line)
            for i in range(0,len(parts),2):
                # One pass prevents overlapping URL prefixes from being rewritten twice.
                pattern='|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True))
                parts[i]=re.sub(pattern,lambda m:mapping[m[0]],parts[i])
            out.append(''.join(parts))
        text=''.join(out);file.write_text(text)
        changes += [{'file':str(file.relative_to(root)),'from':u,'to':v} for u,v in mapping.items()]
    errors += [{'file':str(file.relative_to(root)),'error':e} for e in validate_reference_language(text.split('---',2)[-1],lang,context)]
report={'files':len(files),'references':count,'internal_article_references':internal,'changes':changes,'errors':errors}
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:sys.exit(1)
