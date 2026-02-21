---
name: hexo-theme-change
description: Modify Hexo theme source code to add custom pages, templates, or features.
license: Apache-2.0
metadata:
  author: Claude
  version: "2.0"
---

# Hexo Theme Modification Skill

Modify Hexo theme source code to add custom pages, templates, layouts, or features. This skill covers theme customization at the source level, not just configuration changes.

## Prerequisites

1. **Dependencies**: Git, Node.js, Hexo CLI, basic HTML/CSS/EJS (or Pug/Stylus) knowledge
2. **Theme Structure**: Familiarity with Hexo theme directory structure

    **Theme Directory Layout**:
    ```
    themes/your-theme/
    ├── layout/          # Template files (EJS/Pug/Swig)
    │   ├── index.ejs    # Homepage template
    │   ├── post.ejs     # Post template
    │   ├── page.ejs     # Page template
    │   ├── archive.ejs  # Archive template
    │   ├── tag.ejs      # Tag page template
    │   ├── category.ejs # Category page template
    │   └── _partial/    # Partial templates
    │       ├── header.ejs
    │       ├── footer.ejs
    │       └── sidebar.ejs
    ├── source/          # Static assets
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── scripts/         # Hexo scripts (optional)
    └── _config.yml      # Theme configuration
    ```

## Common Modifications

### 1. Add a Custom Page

Create a new standalone page (e.g., portfolio, friends links, about page with custom layout).

**Step 1: Create page layout template**
```bash
# Create new layout file
touch themes/your-theme/layout/custom-page.ejs
```

Example `custom-page.ejs`:
```ejs
<%- partial('_partial/header') %>
<main class="custom-page">
  <article class="page-content">
    <h1 class="page-title"><%= page.title %></h1>
    <div class="page-body">
      <%- page.content %>
    </div>
  </article>
</main>
<%- partial('_partial/footer') %>
```

**Step 2: Create page source file**
```bash
# Create page in Hexo source
hexo new page "portfolio"
```

**Step 3: Specify layout in front-matter**
Edit `source/portfolio/index.md`:
```markdown
---
title: Portfolio
layout: custom-page  # Use custom layout
date: 2024-01-01
---

Your portfolio content here.
```

### 2. Add a New Partial Template

Create reusable template components.

**Step 1: Create partial file**
```bash
touch themes/your-theme/layout/_partial/comments.ejs
```

Example `comments.ejs`:
```ejs
<% if (theme.comments && theme.comments.enabled) { %>
<section id="comments" class="comments-section">
  <div id="comment-container"></div>
  <script>
    // Comment system initialization
  </script>
</section>
<% } %>
```

**Step 2: Include in main templates**
Edit `themes/your-theme/layout/post.ejs`:
```ejs
<%- partial('_partial/header') %>
<article class="post">
  <h1><%= page.title %></h1>
  <%- page.content %>
</article>
<%- partial('_partial/comments') %>  <!-- Include comments partial -->
<%- partial('_partial/footer') %>
```

### 3. Modify Existing Template

Customize how posts, archives, or other pages render.

**Example: Add reading time to posts**

Edit `themes/your-theme/layout/post.ejs`:
```ejs
<article class="post">
  <header class="post-header">
    <h1 class="post-title"><%= page.title %></h1>
    <div class="post-meta">
      <span class="post-date"><%= date(page.date, 'YYYY-MM-DD') %></span>
      <!-- Add reading time -->
      <span class="reading-time">
        <% var words = strip_html(page.content).length; %>
        <% var minutes = Math.ceil(words / 300); %>
        <%= minutes %> min read
      </span>
    </div>
  </header>
  <div class="post-content">
    <%- page.content %>
  </div>
</article>
```

### 4. Add Custom CSS/JS

**Option A: Modify existing files**
```bash
# Edit theme styles
themes/your-theme/source/css/style.css

# Edit theme scripts
themes/your-theme/source/js/main.js
```

**Option B: Add new files and include them**

Create file: `themes/your-theme/source/css/custom.css`

Include in layout (e.g., `layout/_partial/head.ejs`):
```ejs
<%- css('css/custom') %>
```

Or for JS: `themes/your-theme/source/js/custom.js`
```ejs
<%- js('js/custom') %>
```

### 5. Add a Custom Post Type

Create different layouts for different content types.

**Step 1: Create layout**
```bash
touch themes/your-theme/layout/photo-post.ejs
```

**Step 2: Use in post front-matter**
```markdown
---
title: My Photo Gallery
layout: photo-post
date: 2024-01-01
photos:
  - url: /images/photo1.jpg
    caption: Photo 1
  - url: /images/photo2.jpg
    caption: Photo 2
---
```

**Step 3: Access in template**
```ejs
<div class="photo-gallery">
  <% page.photos.forEach(function(photo) { %>
    <figure class="photo-item">
      <img src="<%= photo.url %>" alt="<%= photo.caption %>">
      <figcaption><%= photo.caption %></figcaption>
    </figure>
  <% }); %>
</div>
```

### 6. Modify Archive/List Layout

Customize how post lists are displayed.

Edit `themes/your-theme/layout/archive.ejs` or `themes/your-theme/layout/index.ejs`:
```ejs
<%- partial('_partial/header') %>

<div class="post-list">
  <% page.posts.forEach(function(post) { %>
    <article class="post-item">
      <h2 class="post-title">
        <a href="<%- url_for(post.path) %>"><%= post.title %></a>
      </h2>
      <div class="post-meta">
        <time datetime="<%= date_xml(post.date) %>">
          <%= date(post.date, 'MMM DD, YYYY') %>
        </time>
        <% if (post.tags && post.tags.length) { %>
          <span class="post-tags">
            <% post.tags.forEach(function(tag) { %>
              <a href="<%- url_for(tag.path) %>">#<%= tag.name %></a>
            <% }); %>
          </span>
        <% } %>
      </div>
      <% if (post.excerpt) { %>
        <p class="post-excerpt"><%= strip_html(post.excerpt) %></p>
      <% } %>
    </article>
  <% }); %>
</div>

<%- partial('_partial/pagination') %>
<%- partial('_partial/footer') %>
```

## Helper Functions Reference

Common Hexo template helpers:

| Helper | Description | Example |
|--------|-------------|---------|
| `url_for(path)` | Generate URL | `<a href="<%- url_for('/about') %>">` |
| `date(date, format)` | Format date | `<%= date(page.date, 'YYYY-MM-DD') %>` |
| `date_xml(date)` | XML date format | `<time datetime="<%= date_xml(post.date) %>">` |
| `strip_html(content)` | Remove HTML tags | `<%= strip_html(post.excerpt) %>` |
| `truncate(text, length)` | Truncate text | `<%= truncate(post.content, {length: 100}) %>` |
| `partial(path, locals)` | Include partial | `<%- partial('_partial/header') %>` |
| `css(path)` | Include CSS | `<%- css('css/style') %>` |
| `js(path)` | Include JS | `<%- js('js/main') %>` |

## Available Variables

| Variable | Description | Scope |
|----------|-------------|-------|
| `site` | Site-wide data | All |
| `site.posts` | All posts | All |
| `site.pages` | All pages | All |
| `site.categories` | All categories | All |
| `site.tags` | All tags | All |
| `page` | Current page data | Page-specific |
| `page.title` | Page/post title | Page-specific |
| `page.content` | Page/post content | Page-specific |
| `page.date` | Post date | Post |
| `page.excerpt` | Post excerpt | Post |
| `page.categories` | Post categories | Post |
| `page.tags` | Post tags | Post |
| `config` | Site configuration | All |
| `theme` | Theme configuration | All |

## Testing Changes

After modifying theme files:

```bash
# Clean cache
hexo clean

# Generate and serve locally
hexo server --debug

# Check for errors in console output
```

## Best Practices

1. **Backup before modifying**: Copy original files before editing
2. **Use partials**: Break templates into reusable components
3. **Check conditionals**: Always check if variables exist before using
4. **Test responsive**: Verify changes on different screen sizes
5. **Keep customizations organized**: Use consistent naming conventions
