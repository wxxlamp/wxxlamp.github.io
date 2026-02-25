# WXX Theme

A responsive Hexo theme optimized for both desktop and mobile, based on the Polar Bear theme with extensive mobile improvements.

## Features

### Core Features
- **Responsive Design**: Fully optimized for desktop, tablet, and mobile devices
- **Fixed Header**: Sticky navigation header for easy access to menu items
- **Fixed Sidebar**: Right-side widget area on desktop that stays visible while scrolling
- **Table of Contents (TOC)**: Auto-generated TOC for posts, fixed position on desktop
- **Reading Progress Bar**: Visual indicator showing reading progress
- **Back to Top Button**: Quick scroll-to-top functionality
- **RSS Feed Support**: Built-in RSS link in navigation

### Mobile Optimizations

#### Header
- Fixed header with reduced height for mobile (50px on mobile, 45px on small screens)
- Centered logo and navigation menu
- Touch-friendly navigation buttons with hover effects

#### Typography & Spacing
- **Line Height**: Optimized `1.85` line height for comfortable reading on mobile
- **Paragraph Spacing**: `1.2em` margin between paragraphs
- **Heading Styles**: Consistent with desktop (H1: bottom border 2px, H2: bottom border 1px, H3: left border 3px)
- **List Spacing**: `0.5em` between list items with `1.7` line height
- **Blockquotes**: Left border with background color matching theme

#### Layout Adjustments
- Content margin-top: `75px` on mobile (accounts for fixed header)
- Horizontal padding: `15px` on mobile, `12px` on small screens
- Full-width layout with proper box-sizing

#### Component Optimizations
- **Code Blocks**: Horizontal scroll with `-webkit-overflow-scrolling: touch`, rounded corners
- **Images**: Full width with rounded corners, proper margins
- **Tables**: Horizontal scroll for overflow content
- **Archive Page**: Year headings with bottom border, improved post list spacing
- **Categories/Tags**: Button-style tags with touch feedback

### Typography

#### Font Stack
- Primary: `'Smiley Sans Oblique', 'Open Sans', 'Helvetica Neue', Arial, sans-serif`
- Code: `'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace`

#### Font Sizes (Mobile)
- Body: `15px` (mobile), `14.5px` (small screens)
- Article Title: `1.35em`
- H1: `1.5em`
- H2: `1.3em`
- H3: `1.15em`
- H4: `1.05em`

### Breakpoints
- Desktop: > 1200px (shows TOC and fixed sidebar)
- Tablet: 769px - 1024px (fluid layout, no fixed sidebar)
- Mobile: 480px - 768px (mobile optimizations)
- Small Mobile: 375px - 480px (compact layout)
- Extra Small: < 375px (minimal layout)

### Special Pages
- **Resume Page**: Password-protected resume layout with PDF export
- **About Page**: Clean profile layout
- **Archive Page**: Year-based organization with styled headings
- **Categories/Tags**: Visual tag cloud with hover effects

## Installation

1. Clone or download this theme to your Hexo themes directory:
```bash
git clone <repository-url> themes/wxx-theme
```

2. Update your `_config.yml`:
```yaml
theme: wxx-theme
```

3. Install dependencies:
```bash
npm install
```

## Configuration

### Site Configuration (_config.yml)
```yaml
theme: wxx-theme

# Theme-specific configuration in _config.wxx-theme.yml
```

### Theme Configuration (_config.wxx-theme.yml)
```yaml
# Menu navigation
menu:
  Archives: /archives
  About: /about
  Resume: /resume

# Theme color
theme:
  color: Default  # Options: Default, Mint Green, Cobalt Blue, Hot Pink, Dark Violet

# Social links
social:
  github: your-github
  twitter: your-twitter

# Analytics (optional)
google_analytics: GA_MEASUREMENT_ID
```

## Customization

### Custom Styles
Add custom SCSS to `source/css/_custom/custom.scss`

### Color Scheme
Edit `$theme-color-map` in `source/css/_variables.scss` to add custom colors.

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome for Android)

## Credits
Based on the [Polar Bear](https://github.com/frostfan/hexo-theme-polarbear) theme by frostfan.

## License
MIT
