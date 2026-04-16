# Markdown Language Polisher

A Claude Code skill that automatically polishes markdown articles by learning from your blog's category-specific language patterns.

## Features

- **Automatic Style Learning**: Scans your existing blog posts to learn category-specific language characteristics
- **Content Enhancement**: Improves sentence flow, logical coherence, and expression richness
- **Error Correction**: Identifies and fixes spelling mistakes, factual errors, and technical terminology
- **Syntax Optimization**: Ensures proper Markdown formatting for code and command-line examples
- **Auto-Update Hook**: Automatically refreshes the language model when new articles are added

## Installation

Place the entire `markdown-language-polisher` folder in your Claude Code skills directory (typically `~/.claude/skills/`).

## Usage

```
/markdown-language-polisher path/to/your-markdown-file.md
```

Optionally specify a category explicitly:
```
/markdown-language-polisher path/to/your-markdown-file.md --category="Your Category"
```

## How It Works

1. **Learning Phase**: The skill scans all markdown files in `source/_posts/` and groups them by category from frontmatter
2. **Pattern Extraction**: Analyzes each category to extract:
   - Writing tone (formal/informal/technical/casual)
   - Sentence structure preferences
   - Vocabulary and terminology patterns
   - Expression styles
3. **Application**: Applies category-specific patterns to polish your target markdown file
4. **Output**: Saves polished content to a new file (original-filename-polished.md)

## Automatic Updates

The skill monitors the `source/_posts/` directory for new articles. When new articles are added, it automatically refreshes its language model to incorporate your evolving writing style.

## Supported Processing Tasks

- **Language Polishing**: Improves sentence flow and readability while maintaining category-appropriate tone
- **Content Expansion**: Adds relevant details without changing core meaning
- **Error Correction**: Fixes spelling mistakes, factual errors, and technical terminology
- **Code/Command Formatting**: Ensures proper Markdown syntax for code snippets and command-line examples

### Example Corrections:
- Converts `claude -p 'test'` to `` `claude -p 'test'` ``
- Fixes "神经王络" to "神经网络"
- Improves sentence structure to match your established patterns

## Requirements

- Node.js >= 14.0.0
- Access to your blog's `source/_posts/` directory

## Directory Structure

```
markdown-language-polisher/
├── SKILL.md           # Skill definition and description
├── skill.json         # Skill configuration and hooks
├── scripts/
│   └── markdown-language-polisher.js  # Main processing script
└── cache/            # Auto-generated cache for language patterns
```