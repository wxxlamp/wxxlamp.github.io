---
name: md-image-migrator
description: 迁移 Markdown 文件中的远程图片到图床，自动下载、上传并替换 URL
license: Apache-2.0
metadata:
  author: wxx
  version: "1.0"
---

# Markdown Image Migrator Skill

此技能用于将 Markdown 文件中的远程图片（如语雀、GitHub 等）迁移到图床，自动完成下载、上传和 URL 替换。

## 前置依赖

1. **img-uploader 技能**: 必须先安装并配置好
   ```bash
   ls .claude/skills/img-uploader/
   ```

2. **Python 依赖**:
   ```bash
   pip install requests
   ```

3. **图床配置**: 根据 img-uploader 的要求配置好 Imgur/GitHub/sm.ms 的 token

## 用法

```bash
python3 .claude/skills/md-image-migrator/md-image-migrator.py <markdown文件> [选项]
```

### 参数

- `<file>`: Markdown 文件路径 (必需)
- `--provider`: 图床提供商 - `imgur` | `smms` | `github` (默认: `imgur`)
- `--dry-run`: 预览模式，只显示找到的图片，不执行下载和上传

### 示例

**基础用法** (使用默认 Imgur):
```bash
python3 .claude/skills/md-image-migrator/md-image-migrator.py \
  source/_posts/cross-border-ecommerce-transaction-flow.md
```

**使用 GitHub 图床**:
```bash
python3 .claude/skills/md-image-migrator/md-image-migrator.py \
  source/_posts/article.md \
  --provider github
```

**预览模式** (查看有哪些图片):
```bash
python3 .claude/skills/md-image-migrator/md-image-migrator.py \
  source/_posts/article.md \
  --dry-run
```

## 工作流程

1. **扫描**: 读取 Markdown 文件，提取所有远程图片 URL
2. **下载**: 将图片下载到临时目录
3. **上传**: 调用 img-uploader 上传到指定图床
4. **替换**: 将 Markdown 中的原 URL 替换为新图床 URL
5. **保存**: 更新 Markdown 文件

## 输出示例

```
找到 9 个远程图片链接
--------------------------------------------------

[1/9] 处理: https://cdn.nlark.com/yuque/0/2026/png/719664/1767518916...
  ✅ 已下载: a1b2c3d4.png
  ✅ 已上传: https://i.imgur.com/xyz12345.png

[2/9] 处理: https://cdn.nlark.com/yuque/0/2026/png/719664/1767518919...
  ✅ 已下载: e5f6g7h8.png
  ✅ 已上传: https://i.imgur.com/abc67890.png

==================================================
✅ 完成! 已替换 9 个图片链接
文件已更新: source/_posts/article.md
```

## 注意事项

1. **备份**: 建议先备份原始文件，或确保文件已 git 提交
2. **网络**: 下载和上传需要稳定的网络连接
3. **Token 限制**: 注意 Imgur 等图床可能有上传频率限制
4. **失败处理**: 如果某个图片上传失败，会跳过并继续处理其他图片
