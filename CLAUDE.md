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

### File Organization

```
├── _config.yml              # Hexo main configuration
├── package.json             # Node.js dependencies
├── source/                  # Blog content
│   ├── _posts/              # Markdown blog posts
│   ├── about/               # About page
│   ├── resume/              # Resume page (Chinese/English with password protection)
│   ├── favicon.ico          # Custom website icon
│   └── CNAME                # Custom domain config (must be in source/)
├── themes/                  # Hexo themes
│   └── wxx-theme/           # Current theme (customized from polarbear)
│       ├── _config.yml      # Theme configuration
│       ├── layout/          # Swig templates
│       └── source/css/      # Theme styles (SCSS)
│           ├── _variables.scss      # Global variables and breakpoints
│           └── _custom/custom.scss  # Custom responsive styles
├── scaffolds/               # Post templates
└── .github/workflows/       # CI/CD configuration
```

### Key Technical Details

- **Language**: Chinese (zh-CN)
- **Custom domain**: wxxlamp.cn (CNAME file must be in `source/` directory)
- **Theme features**: Fixed header, fixed sidebar (desktop), responsive mobile layout with breakpoints at 768px, 480px, 375px
- **Analytics**: Busuanzi (visitor count) configured in footer
- **Fonts**: Smiley Sans Oblique (asynchronous loading) with system font stack fallback
- **Features**: Mobile-responsive, TOC (Table of Contents), reading progress bar, RSS feed

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
   - Types: feat, fix, docs, style, refactor, test, chore, ci, perf, revert
   - Examples:
     - `feat(blog): Add new article about MBP configuration`
     - `fix(theme): Correct mobile header spacing`
     - `style(content): Replace quotes in description`
     - `refactor(scss): Optimize responsive breakpoints`

## Theme Development

### Custom Styles

Mobile-responsive styles are in `themes/wxx-theme/source/css/_custom/custom.scss`:
- Fixed header with shadow
- Fixed sidebar on desktop (hidden on mobile < 1024px)
- Responsive breakpoints: 768px, 480px, 375px
- Typography optimized for mobile (line-height 1.85)
- Asynchronous font loading with system font fallbacks

### CSS Preprocessors

The theme uses SCSS for styling. Follow these guidelines:
- Use kebab-case for class names
- Follow BEM methodology for modular CSS
- Optimize for performance by minimizing redundant styles
- Ensure responsive design across all device sizes

### Widget Configuration

Enable/disable sidebar widgets in `themes/wxx-theme/_config.yml`:
```yaml
widget:
  Tags: true
  Categories: true
  Custom: false
```

Color themes can be configured in `themes/wxx-theme/_config.yml`:
```yaml
theme:
  color: Default  # Options: Default | Mint Green | Cobalt Blue | Hot Pink | Dark Violet
```

### Important Files for Theme Changes

- `themes/wxx-theme/source/css/_custom/custom.scss` - Custom styles (mobile responsive)
- `themes/wxx-theme/source/css/_variables.scss` - Global variables and breakpoints
- `themes/wxx-theme/layout/` - Swig templates
- `themes/wxx-theme/_config.yml` - Theme settings
- `themes/wxx-theme/languages/` - Localization files

## Package Management

The project uses npm for dependency management with the following scripts:
- `npm run server` - Start local development server
- `npm run build` - Generate static files
- `npm run clean` - Clean cache and generated files
- `npm run deploy` - Deploy to remote

Key dependencies include:
- Hexo 8.x core
- Renderers: marked, ejs, stylus, swig, sass
- Generators: archive, category, feed, index, tag
- Server module for local development

## Testing and Validation

- Always test locally using `npm run server` before committing changes
- Verify responsive layouts across different screen sizes
- Check all interactive elements work properly
- Validate that all pages load correctly and external links function
- Confirm RSS feed and analytics are working

## Important Notes

- **CNAME must be in `source/`**: Hexo only copies `source/` directory contents to `public/`. The CNAME file for custom domain must be at `source/CNAME`.
- **Do not commit generated files**: `db.json`, `public/`, `.deploy_git` are generated and should not be committed.
- **Test locally before pushing**: Run `hexo server` to preview changes locally.
- **Mobile-first**: This theme has extensive mobile optimizations - test responsive layouts when making CSS changes.
- **Font loading**: Theme uses asynchronous font loading to improve performance - test font rendering on different browsers and connection speeds.
