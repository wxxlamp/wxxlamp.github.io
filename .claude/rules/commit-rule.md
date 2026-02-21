# Git提交规范规则

## 提交类型规范
- feat: 新功能(feature)的添加
- fix: 修复bug
- docs: 文档(documentation)更新
- style: 不影响代码逻辑的格式调整(空格, 缺少分号等)
- refactor: 代码重构，既不修复bug也不添加功能
- test: 测试相关代码的添加或修改
- chore: 构建过程或辅助工具的变动
- perf: 性能优化
- ci: CI配置文件和脚本的修改
- revert: 回退版本

## 提交格式
- 格式: `<type>(<scope>): <subject>`
- type: 必须是上述类型之一
- scope: 可选，影响范围描述，例如(module), (theme), (build)等
- subject: 简短描述，不超过50个字符，使用祈使句，首字母大写，末尾无句号

## 详细要求
- 提交信息必须使用中文或英文，保持与项目语言一致
- 主题(subject)应当简洁明了地描述修改内容
- 需要时可在主体部分详细描述修改原因和解决方案
- 关联issue应在提交信息底部添加"Fixes #issue-number"或"Closes #issue-number"
- 避免空白或过于简单的提交信息