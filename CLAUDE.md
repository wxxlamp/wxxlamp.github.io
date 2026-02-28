# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Hexo-generated static blog** deployed to GitHub Pages at `wxxlamp.cn`.

- **Live site**: https://wxxlamp.cn
- **Platform**: GitHub Pages
- **Generator**: Hexo 8.x
- **Theme**: wxx-theme (renamed from polarbear with mobile optimizations)

## Architecture

### Branch Structure

- `deploy`: Source branch - Contains Hexo source files (markdown, config, themes)
- `main`: Contains generated static HTML files for GitHub Pages deployment
- `test`: Development branch for testing theme changes

### File Organization

```
├── _config.yml              # Hexo main configuration
├── package.json             # Node.js dependencies
├── source/                  # Blog content
│   ├── _posts/              # Markdown blog posts
│   ├── about/               # About page
│   ├── resume/              # Resume page
│   └── CNAME                # Custom domain config (must be in source/)
├── themes/                  # Hexo themes
│   └── wxx-theme/           # Current theme (customized from polarbear)
│       ├── _config.yml      # Theme configuration
│       ├── layout/          # Swig templates
│       └── source/css/      # Theme styles (SCSS)
├── scaffolds/               # Post templates
└── .github/workflows/       # CI/CD configuration
```

### Key Technical Details

- **Language**: Chinese (zh-CN)
- **Custom domain**: wxxlamp.cn (CNAME file must be in `source/` directory)
- **Theme features**: Fixed header, fixed sidebar (desktop), responsive mobile layout
- **Analytics**: Busuanzi (visitor count) configured in footer

## Common Operations

### Local Development

```bash
# Install dependencies
npm install

# Start local server (default port 4000)
npm run server
# or
hexo server

# Generate static files
npm run build
# or
hexo generate

# Clean cache and generated files
npm run clean
# or
hexo clean
```

### Creating Posts

```bash
hexo new "Post Title"
```

Posts are created in `source/_posts/` with front matter:
```yaml
---
title: Post Title
date: YYYY-MM-DD HH:mm:ss
tags:
  - tag1
categories:
  - category1
---
```

### Deployment

This repository uses GitHub Actions for automated deployment:
1. Push to `deploy` branch
2. GitHub Actions builds the site (`npx hexo generate`)
3. Generated files in `public/` deployed to `main` branch
4. GitHub Pages serves from `main` branch

**Important**: Do NOT push to `main` branch manually - it will be overwritten by the automated deployment.

## Git Workflow Rules

**Critical constraints for Claude Code:**
1. **Never run `git push`**: Always ask the user to manually push changes
2. **Commit process**: Before committing, show `git diff --staged` and ask for confirmation
3. **Commit message format**: `<type>(<scope>): <subject>`
   - Types: feat, fix, docs, style, refactor, test, chore, ci
   - Example: `fix(theme): Correct mobile header spacing`

## Theme Development

### Custom Styles

Mobile-responsive styles are in `themes/wxx-theme/source/css/_custom/custom.scss`:
- Fixed header with shadow
- Fixed sidebar on desktop (hidden on mobile < 1024px)
- Responsive breakpoints: 768px, 480px, 375px
- Typography optimized for mobile (line-height 1.85)

### Widget Configuration

Enable/disable sidebar widgets in `themes/wxx-theme/_config.yml`:
```yaml
widget:
  Tags: true
  Categories: true
  Custom: false
```

### Important Files for Theme Changes

- `themes/wxx-theme/source/css/_custom/custom.scss` - Custom styles (mobile responsive)
- `themes/wxx-theme/layout/` - Swig templates
- `themes/wxx-theme/_config.yml` - Theme settings

## Important Notes

- **CNAME must be in `source/`**: Hexo only copies `source/` directory contents to `public/`. The CNAME file for custom domain must be at `source/CNAME`.
- **Do not commit generated files**: `db.json`, `public/`, `.deploy_git` are generated and should not be committed.
- **Test locally before pushing**: Run `hexo server` to preview changes locally.
- **Mobile-first**: This theme has extensive mobile optimizations - test responsive layouts when making CSS changes.
