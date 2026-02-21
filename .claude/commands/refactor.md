# 博客系统重构命令

## 项目目标
对现有的Hexo博客系统进行全面重构，包括主题更换、部署流程优化和图片管理改进。

## 重要注意事项
在开始重构前，请注意当前deploy分支包含的是hexo编译后的HTML文件，而不是原始的markdown和配置文件。建议先备份deploy分支内容，然后清空该分支（删除所有静态文件，但保留`.gitignore`、`.claude/`、`.github/workflows/`等配置文件），并重新配置为存放源码（包括markdown文件、Hexo配置文件等），而让GitHub Actions将编译后的HTML文件部署到master分支。

## 重构任务

### 1. 主题更换
- 将当前主题替换为polarbear主题
- 地址：https://github.com/frostfan/hexo-theme-polarbear
- 保留现有内容和配置
- 根据需要进行自定义修改
- 进行全面的功能验证

### 2. 部署流程优化
- 实现在deploy分支编写博客
- 配置GitHub Actions自动化构建
- 将编译后的文件部署到master分支
- 确保CI/CD流程稳定可靠

### 3. 图片管理优化
- 配置Imgur图床Client ID（需要用户提供Client ID）
- 将每篇MD文档中的本地图片上传到Imgur图床
- 更新文档中的图片链接指向图床地址
- 保持文档格式完整性
- 确保图片正常展示

## 执行顺序

1. **备份当前deploy分支内容**
   - 确保现有HTML静态文件已备份或已部署到生产环境

2. **清空deploy分支**
   - **删除所有Hexo生成的静态文件**：
     - HTML文件（根目录和子目录中的`index.html`、`*.html`）
     - CSS文件（`css/`、`style.css`等）
     - JS文件（`js/`、`*.js`）
     - 图片（`images/`、`assets/img/`等）
     - 字体（`fonts/`）
     - 文章页面（`20*/`等日期目录）
     - 归档页面（`archives/`）
     - 标签/分类页面（`tags/`、`categories/`）
     - 其他页面（`about/`、`links/`等）
   - **保留以下文件/目录**：
     - `.gitignore` - Git忽略规则
     - `.claude/` - Claude配置和技能
     - `.github/workflows/` - GitHub Actions工作流配置
     - `CNAME` - 自定义域名配置（可选）
     - `README.md` - 项目说明（可选）
   - **说明**：清空后deploy分支将用于存储博客源码（markdown、配置文件、主题文件等）

3. **创建test分支进行主题更换实验**
   - 从清空的deploy分支创建test分支
   - 安装polarbear主题并进行初始配置
   - 在test分支中验证主题功能正常

4. **验证通过后合并到deploy分支**
   - test分支验证无误后，合并到deploy分支
   - 开始使用新主题进行日常博客编写

5. **配置本地开发环境**
   - 配置Hexo本地预览环境
   - 确保主题渲染正常

6. **配置Imgur图床Client ID**（需要用户提供Client ID）
   - 访问 https://api.imgur.com/oauth2/addclient 注册应用获取Client ID
   - 复制`.claude/skills/img-uploader/config.json.example`为`config.json`
   - 填写`imgur_client_id`和`default_provider`

7. **实施图片上传功能**
   - 将每篇MD文档中的本地图片上传到Imgur图床
   - 更新文档中的图片链接

8. **设置GitHub Actions部署流程**
   - 配置自动化构建
   - 将编译后的HTML文件部署到master分支

9. **进行全面测试**
   - 验证所有页面、链接、图片正常

10. **部署到生产环境**
    - 确认GitHub Pages指向master分支

## 执行要求
- 每个步骤完成后必须执行commit保存更改
- 遵循提交信息规范
- 确保每次提交都有明确的变更内容
- 使用commit技能进行提交操作

## 验证标准
- 所有页面正常显示
- 主题样式正确应用
- 图片链接全部有效
- 部署流程自动化运行
- 移动端适配良好
- 加载速度优化