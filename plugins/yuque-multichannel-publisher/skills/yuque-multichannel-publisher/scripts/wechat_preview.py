#!/usr/bin/env python3
"""Capture mobile previews; output evidence, never auto-approve visual quality."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from editorial_quality import digest


def capture(project):
    source = project/'draft/wechat.html'
    destination=project/'draft/preview'
    destination.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch()
        try:
            for width in (375,430):
                page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
                page.set_content('<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+source.read_text()+'</body></html>',wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                metrics=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth, brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)})''')
                path=destination/f'wechat-{width}.png'
                page.screenshot(path=str(path),full_page=True)
                results.append({'width':width,'path':path.relative_to(project).as_posix(),'sha256':digest(path),'html_sha256':digest(source),**metrics})
                page.close()
        finally:
            browser.close()
    payload={'status':'needs-visual-review','previews':results}
    (destination/'layout-evidence.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    return payload

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-dir',required=True)
    args=parser.parse_args()
    print(json.dumps(capture(Path(args.project_dir).resolve()),ensure_ascii=False,indent=2))
