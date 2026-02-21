我希望对本地基于hexo主题的博客系统进行重构。具体来说：
1. 将现有的主题替换为 https://github.com/frostfan/hexo-theme-polarbear，同时有可能对替换后的主题进行修改和验证
2. 在deploy分支写博客，然后通过github actions将编译后的文件部署到master分支
3. 将每篇md文档中的图片都上传到一个免费的图床（S.EE），同时修改md文档中文件的位置，保证文件正常展示

我希望在项目初期，你帮我生成一些commands,skills和rules。包括但是不限于：

1. rules:
   1. front-dev-rule.md，用于修改主题编写js相关代码时候的规范
   2. git-workflow.md git提交时候的一些规范（已经生成）
   3. skill-structure-rule.md 技能文件组织规范
   4. github-actions-deploy-rule.md GitHub Actions部署规范
   5. commit-rule.md 提交规范

2. skills:
   1. hexo-theme-change，用于修改对应主题时候需要的skill，主要负责按照我的要求进行代码编写、测试和验证，需要用到local-validator skill
      - 技能文件应该放在单独的目录中，使用 SKILL.md 作为描述文件
   2. local-validator，用于主题修改完之后本地页面验证
      - 技能文件应该放在单独的目录中，使用 SKILL.md 作为描述文件
   3. img-uploader, 用于将不在图床的图片上传到图床（S.EE），并修改md文件的链接
      - 技能文件应该放在单独的目录中，使用 SKILL.md 作为描述文件
   4. github-actions-deploy, 用于配置GitHub Actions自动化部署
      - 技能文件应该放在单独的目录中，使用 SKILL.md 作为描述文件
   5. commit, 用于执行提交操作
      - 技能文件应该放在单独的目录中，使用 SKILL.md 作为描述文件

3. commands：
   1. refactor.md 用于描述我的需求

执行完上述操作后，请立即进行git commit提交更改。

注意：上面提到的rules、skills和commands可能不完全，你可以补充