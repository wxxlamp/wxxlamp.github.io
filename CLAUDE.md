# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Hexo-generated static blog** deployed to GitHub Pages at `wxxlamp.cn`. The repository contains only the **generated HTML output**, not the Hexo source files.

- **Live site**: https://wxxlamp.cn
- **Platform**: GitHub Pages
- **Generator**: Hexo 5.2.0
- **Theme**: Anatole-Wxx (customized fork of Anatole)

## Architecture

### Branch Structure

- `main`: Source branch (likely contains Hexo source in a separate repository)
- `deploy` (current): Contains generated static HTML files for GitHub Pages deployment
- `master`: Legacy branch (older GitHub Pages default)

### File Organization

This repo contains pre-built static files only:

```
├── index.html                    # Homepage with post listings
├── CNAME                         # Custom domain: wxxlamp.cn
├── {year}/{month}/{day}/         # Blog posts in dated directories
│   └── {post-slug}/
│       └── index.html            # Individual post HTML
├── archives/                     # Archive pages by year
├── categories/                   # Category listing pages
├── tags/                         # Tag listing pages
├── about/                        # About page + resume HTML files
│   ├── index.html
│   ├── resume.html               # Personal resume (password protected)
│   └── resume_en_US.html         # English resume
├── links/                        # Friends/links page
├── css/                          # Stylesheets
│   ├── style.css                 # Main theme styles
│   ├── blog_basic.css            # Blog-specific styles
│   └── font-awesome*.css         # Icon fonts
├── js/                           # JavaScript files
│   ├── jquery.js                 # jQuery dependency
│   ├── tagcanvas.js              # Tag cloud animation
│   ├── visitors.js               # Visitor counter (LeanCloud)
│   └── baidu-tongji.js           # Baidu Analytics
├── images/                       # Site images
├── fonts/                        # Custom fonts
└── assets/img/                   # Assets (favicon, etc.)
```

### Key Technical Details

- **All files are static HTML**: No server-side processing
- **Chinese language content**: Primary language is Chinese (zh-CN)
- **jQuery-based**: Uses jQuery for DOM manipulation and animations
- **Valine comments**: Comment system uses LeanCloud/Valine (configured in post HTML)
- **Baidu Analytics**: Traffic tracking via Baidu Tongji
- **Font Awesome**: Icon font library

## Common Operations

### Viewing Changes Locally

Since these are static HTML files, open them directly in a browser:

```bash
open index.html
# Or serve with a simple HTTP server:
python3 -m http.server 8000
```

### Deploying Updates

This repository receives generated files from the Hexo source repository. The typical workflow:

1. Edit content in the Hexo source repository (not this repo)
2. Run `hexo generate` to build static files
3. Copy generated files to this repository
4. Commit and push to the `deploy` branch

```bash
# After copying generated files:
git add .
git commit -m "Update site content"
git push origin deploy
```

### GitHub Pages Configuration

- Custom domain configured via `CNAME` file: `wxxlamp.cn`
- ICP备案: 豫ICP备20004458号-1
- 公安备案: 豫公网安备 44030400004458号

## Important Notes

- **Do not edit HTML directly** for content changes - edits will be overwritten on next Hexo build
- **Direct HTML edits** should only be for:
  - Emergency fixes to generated output
  - Custom pages not managed by Hexo (e.g., `about/resume.html`)
  - Style/script updates in `css/` or `js/`
- The source Hexo repository with markdown content is separate: https://github.com/wxxlamp/anatole-core-wxx
