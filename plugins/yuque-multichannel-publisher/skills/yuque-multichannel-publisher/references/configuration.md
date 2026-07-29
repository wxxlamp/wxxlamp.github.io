# 便携配置

## 依赖

插件只有一个主 Skill，Python 运行依赖位于该 Skill 的 `requirements.txt`：

```bash
python3 -m pip install -r <skill-root>/requirements.txt
playwright install chromium
```

`playwright` 只用于首次登录或登录态失效；`requests` 用于语雀和图床 HTTP 请求。

## 工作区

在目标博客或内容仓库根目录执行：

```bash
python3 <skill-root>/scripts/pipeline.py setup
```

默认生成 `.codex/yuque-multichannel-publisher/config.json`。如果脚本无法自动识别工作区，设置：

```bash
YMP_WORKSPACE_ROOT=/absolute/project/path
```

默认目录：

```json
{
  "posts_dir": "source/_posts",
  "content_projects_dir": "content-projects",
  "wechat_dir": "wechat",
  "rednote_dir": "rednote",
  "image_provider": "imgur"
}
```

目录可修改，但 `posts_dir` 应位于工作区内，以便语气样本使用稳定的相对路径。

## 图床凭据

优先使用环境变量，不把 token 写进插件：

- Imgur：`IMGUR_CLIENT_ID`
- SM.MS：`SMMS_TOKEN`
- GitHub：`IMAGE_UPLOADER_GITHUB_TOKEN`、`IMAGE_UPLOADER_GITHUB_OWNER`、`IMAGE_UPLOADER_GITHUB_REPO`
- Chevereto：`CHEVERETO_API_KEY`、`CHEVERETO_URL`

也可以把对应字段写进工作区本地 `config.json`。该目录必须加入 `.gitignore`：

```gitignore
.codex/yuque-multichannel-publisher/
```

GitHub 图床还支持：

```json
{
  "github_path": "images",
  "github_branch": "main",
  "github_cdn": "jsdelivr"
}
```

`github_cdn` 可选 `jsdelivr` 或 `china`。

## 复制分发

分发时只复制整个 `yuque-multichannel-publisher/` 插件目录。不要复制目标工作区的：

- `.codex/yuque-multichannel-publisher/`
- `content-projects/`
- 图床 token
- 语雀 `storage_state.json`

接收者在自己的工作区执行 `setup`，首次使用相关分类时由 AI 建立自己的语气档案。
