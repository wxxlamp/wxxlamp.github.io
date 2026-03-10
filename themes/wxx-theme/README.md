# WXX Theme

基于 [Polar Bear](https://github.com/frostfan/hexo-theme-polarbear) 深度定制的 Hexo 主题，针对移动端体验进行了大量优化。

## 特性

### 核心功能
- **响应式布局**：完整适配桌面、平板、手机设备
- **固定顶栏**：滚动时导航始终可见
- **固定侧边栏**：桌面端侧边栏 Widget 区域跟随滚动
- **文章目录（TOC）**：自动生成并固定在桌面端右侧
- **阅读进度条**：顶部进度条实时显示阅读进度
- **回到顶部**：一键滚回页面顶部
- **RSS 支持**：导航栏内置 RSS 链接

### 特殊页面
- **简历页面**：密码保护 + PDF 导出
- **关于页面**：简洁个人介绍布局
- **归档页面**：按年份分组，标题带下划线样式
- **分类/标签页**：按钮式标签云，支持悬停效果

### 断点说明

| 范围 | 布局 |
|------|------|
| > 1200px | 显示 TOC 与固定侧边栏 |
| 769px – 1024px | 流式布局，隐藏固定侧边栏 |
| 480px – 768px | 移动端优化布局 |
| 375px – 480px | 紧凑型布局 |
| < 375px | 极简布局 |

### 移动端优化

- 固定顶栏，移动端高度 50px（小屏 45px）
- 行高 `1.85`，段落间距 `1.2em`，适合长文阅读
- 代码块支持横向滑动（`-webkit-overflow-scrolling: touch`）
- 图片自适应全宽，表格支持横向溢出滚动

### 字体

- 正文：`'Smiley Sans Oblique', 'Open Sans', 'Helvetica Neue', Arial, sans-serif`
- 代码：`'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace`

## 安装

```bash
git clone <repository-url> themes/wxx-theme
```

在 `_config.yml` 中启用：

```yaml
theme: wxx-theme
```

## 配置

主要配置项位于 `themes/wxx-theme/_config.yml`：

```yaml
# 导航菜单
menu:
  Archives: /archives
  About: /about
  Resume: /resume

# 主题配色（Default | Mint Green | Cobalt Blue | Hot Pink | Dark Violet）
theme:
  color: Default

# 侧边栏 Widget
widget:
  Tags: true
  Categories: true
  Custom: false

# 社交链接
social:
  github: your-github

# 统计（不蒜子）
busuanzi: true
```

## 自定义样式

自定义 SCSS 写入 `source/css/_custom/custom.scss`，该文件在构建时自动引入。

修改配色变量请编辑 `source/css/_variables.scss` 中的 `$theme-color-map`。

## 浏览器支持

- Chrome / Edge（最新版）
- Firefox（最新版）
- Safari（最新版）
- iOS Safari / Chrome for Android

## Credits

基于 [Polar Bear](https://github.com/frostfan/hexo-theme-polarbear) by frostfan。

## License

MIT
