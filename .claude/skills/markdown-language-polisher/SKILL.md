---
name: markdown-language-polisher
description: Automatically polishes markdown articles by learning from your blog's category-specific language patterns. When you have a markdown file that needs language refinement, grammar correction, or style matching to your blog's tone, use this skill. It analyzes your existing articles by category to understand your writing style, then applies those patterns to polish new content. Perfect for improving flow, fixing errors, and maintaining consistency across your blog.
---

# Markdown Language Polisher

Automatically polishes markdown articles by learning from your blog's category-specific language patterns.

## Purpose

This skill analyzes your existing markdown articles in `@source/_posts/` to learn category-specific language characteristics, then applies those patterns to polish new or existing markdown content.

## Capabilities

### 1. Language Pattern Learning
- Automatically scans `@source/_posts/` directory
- Groups articles by category (from frontmatter)
- Extracts language patterns for each category:
  - Writing tone (formal/informal/technical/casual)
  - Sentence structure preferences
  - Vocabulary and terminology patterns
  - Expression styles (narrative/argumentative/descriptive/technical)

### 2. Content Processing
Applies learned patterns to target markdown files:

#### Language Polishing
- Improves sentence flow and readability
- Enhances logical coherence
- Maintains category-appropriate tone

#### Content Expansion
- Adds relevant details without changing core meaning
- Improves logical connections between ideas
- Enriches expression while preserving intent

#### Error Correction
- Identifies and fixes spelling mistakes
- Corrects factual errors
- Fixes technical terminology

#### Code/Command Formatting
- Ensures proper markdown syntax for code snippets
- Formats command-line examples with proper backticks
- Example: `claude -p 'test'` instead of plain text

## Usage

```
/markdown-language-polisher path/to/target-file.md
```

Or to specify a category explicitly:
```
/markdown-language-polisher path/to/target-file.md --category="your-category"
```

## Automatic Learning Update

The skill monitors `@source/_posts/` for new additions and automatically updates its language model when new articles are detected, ensuring consistent learning of your evolving writing style.

## Implementation Flow

1. Load existing articles from `@source/_posts/`
2. Categorize articles and extract language patterns
3. Identify target article category (either from frontmatter or argument)
4. Apply category-specific language patterns to polish content
5. Preserve original meaning while improving presentation
6. Output polished markdown with improved formatting