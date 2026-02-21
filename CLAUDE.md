# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Hexo-generated static blog** deployed to GitHub Pages at `wxxlamp.cn`.

- **Live site**: https://wxxlamp.cn
- **Platform**: GitHub Pages
- **Generator**: Hexo 7.x
- **Theme**: polarbear

## Architecture

### Branch Structure

- `deploy`: Source branch - Contains Hexo source files (markdown, config, themes)
- `master`: Contains generated static HTML files for GitHub Pages deployment
- `test`: Development branch for testing theme changes

### File Organization

```
├── _config.yml              # Hexo main configuration
├── _config.polarbear.yml    # Theme configuration
├── package.json             # Node.js dependencies
├── source/                  # Blog content
│   └── _posts/              # Markdown blog posts
├── themes/                  # Hexo themes
│   └── polarbear/           # Current theme
├── scaffolds/               # Post templates
└── .github/workflows/       # CI/CD configuration
```

### Key Technical Details

- **Language**: Chinese (zh-CN)
- **Image hosting**: Imgur
- **Analytics**: (Configure as needed)

## Common Operations

### Local Development

```bash
# Install dependencies
npm install

# Start local server
hexo server

# Generate static files
hexo generate

# Clean cache
hexo clean
```

### Creating Posts

```bash
hexo new "Post Title"
```

### Deployment

This repository uses GitHub Actions for automated deployment:
1. Push to `deploy` branch
2. GitHub Actions builds the site
3. Generated files deployed to `master` branch

## Important Notes

- **Do not commit `config.json`** with API tokens
- **Do not commit `db.json` or `public/`** - these are generated files
- Always test locally with `hexo server` before pushing
