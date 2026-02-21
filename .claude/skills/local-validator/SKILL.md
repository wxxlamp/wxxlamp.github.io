---
name: local-validator
description: Compile and validate Hexo theme modifications locally.
license: Apache-2.0
metadata:
  author: Claude
  version: "2.0"
---

# Local Theme Validator Skill

Compile and validate Hexo theme modifications locally. This skill covers the complete workflow of testing theme changes from source modification to final verification.

## Prerequisites

1. **Dependencies**: Node.js, Hexo CLI, theme source files
2. **Working Directory**: Your Hexo source repository (not the generated static files)

    **Expected Directory Structure**:
    ```
    hexo-blog/
    ├── _config.yml          # Site config
    ├── themes/
    │   └── your-theme/      # Theme being modified
    │       ├── layout/
    │       ├── source/
    │       └── _config.yml  # Theme config
    ├── source/              # Blog content
    └── package.json
    ```

## Theme Development Workflow

### Step 1: Clean Previous Build

Always start with a clean state to avoid cached issues:

```bash
hexo clean
```

This removes:
- `db.json` - Database cache
- `public/` - Generated static files
- `.deploy_git/` - Deployment cache

### Step 2: Generate Site with Debug

Compile the site with error details:

```bash
# Basic generation
hexo generate

# Or with verbose output for debugging
hexo generate --debug

# Watch mode (auto-regenerate on file changes)
hexo generate --watch
```

**Watch for theme-specific errors:**
- Template syntax errors (EJS/Pug)
- Missing partials
- Undefined variables
- Helper function errors

### Step 3: Start Local Server

Serve the generated site locally:

```bash
# Default server
hexo server

# Custom port
hexo server -p 3000

# Allow external access (for mobile testing)
hexo server -i 0.0.0.0

# Include draft posts
hexo server --draft

# Open browser automatically
hexo server -o
```

### Step 4: Validate Theme Changes

Use this checklist to verify modifications:

#### Layout Verification
- [ ] **Homepage** (`/`) renders correctly
- [ ] **Post pages** display proper layout
- [ ] **Archive pages** show post lists
- [ ] **Tag/Category pages** work
- [ ] **Custom pages** (if added) render properly

#### Style Verification
- [ ] CSS changes are applied
- [ ] Responsive design works (test mobile width)
- [ ] No console errors for missing CSS/JS files
- [ ] Theme colors and fonts render correctly

#### Functionality Verification
- [ ] Navigation links work
- [ ] Pagination functions correctly
- [ ] Images load properly
- [ ] Code blocks render with syntax highlighting

#### Partial Template Verification
- [ ] Header/footer display on all pages
- [ ] Sidebars/widgets render correctly
- [ ] Comments section appears (if configured)
- [ ] Analytics scripts load

## Common Theme Issues & Fixes

### Issue: Template Changes Not Reflected

**Cause**: Hexo caches compiled templates

**Fix**:
```bash
hexo clean && hexo server
```

### Issue: CSS/JS Not Updating

**Cause**: Browser cache or Hexo asset pipeline

**Fix**:
1. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+F5` (Windows)
2. Check asset path in template:
   ```ejs
   <%- css('css/style') %>  <!-- Looks in themes/your-theme/source/css/ -->
   ```

### Issue: Partial Not Found

**Cause**: Wrong path or missing file

**Fix**:
```bash
# Verify file exists
ls themes/your-theme/layout/_partial/your-partial.ejs

# Check include path in template
<%- partial('_partial/your-partial') %>
```

### Issue: Variable Undefined Error

**Cause**: Accessing undefined theme config or page variable

**Fix**:
```ejs
<!-- Always check before using -->
<% if (theme.feature && theme.feature.enabled) { %>
  <div class="feature"><%= theme.feature.text %></div>
<% } %>

<!-- For page variables -->
<% if (page.description) { %>
  <meta name="description" content="<%= page.description %>">
<% } %>
```

### Issue: Syntax Error in EJS Template

**Cause**: Malformed EJS syntax

**Fix**:
```bash
# Run with debug to see exact error location
hexo generate --debug

# Common mistakes:
# - Missing closing tag: <%= var %>
# - Wrong tag type: <%= %> vs <%- %> vs <% %>
#   <%= %> - Escaped output
#   <%- %> - Unescaped output (for HTML)
#   <% %>  - Logic only, no output
```

## Debug Commands

### Enable Verbose Logging

```bash
# Debug mode
hexo server --debug

# Silent mode (less noise)
hexo server --silent
```

### Check Theme Configuration

```bash
# List all config values
hexo config theme

# Check specific value
hexo config theme.your_setting
```

### Validate Package Installation

```bash
# Ensure Hexo and theme dependencies are installed
npm list hexo
cd themes/your-theme && npm list  # if theme has its own package.json
```

## Automated Validation (Optional)

Install validation tools for deeper checks:

```bash
# HTML validation
npm install -g htmlhint
htmlhint public/**/*.html

# Link checking (requires generated site)
npm install -g broken-link-checker
blc http://localhost:4000 -ro
```

## Complete Validation Script

Use the provided script: [`validate-theme.sh`](validate-theme.sh)

### Setup

```bash
# Copy script to your Hexo root
cp .claude/skills/local-validator/validate-theme.sh /path/to/your/hexo-blog/

# Make executable
chmod +x validate-theme.sh
```

### Usage

```bash
./validate-theme.sh
```

The script will:
1. Run `hexo clean` to clear caches
2. Run `hexo generate --debug` and capture output
3. Check for errors in build log
4. Start `hexo server` on port 4000
5. Auto-cleanup server on exit

## Quick Reference

| Command | Purpose |
|---------|---------|
| `hexo clean` | Clear all caches |
| `hexo generate` | Build static files |
| `hexo generate --watch` | Auto-rebuild on changes |
| `hexo server` | Start dev server |
| `hexo server --draft` | Include drafts |
| `hexo server -p 3000` | Custom port |
| `hexo server -o` | Auto-open browser |
| `hexo generate --debug` | Verbose build output |

## Best Practices

1. **Always clean before major changes** - `hexo clean`
2. **Test in multiple browsers** - Chrome, Firefox, Safari
3. **Test responsive layouts** - Use browser dev tools
4. **Check console for errors** - Open DevTools → Console
5. **Validate HTML** - Use W3C validator or htmlhint
6. **Commit frequently** - Save working states with git
