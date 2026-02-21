# Git Workflow Rules

## 核心原则
1. **禁止 Push**: 严禁执行 `git push` 或任何将代码推送到远程仓库的操作。当用户请求 push 时，必须拒绝并提醒用户手动执行。
2. **分阶段提交**: 支持分阶段 `git add` 和 `git commit`，不要一次性提交所有更改，除非用户明确指示。
3. **自动消息生成**: 执行 commit 时，必须分析 `git diff --staged` 的内容，生成符合 Conventional Commits 规范的提交信息。

## 提交流程强制约束
在执行任何 `git commit` 操作之前，必须遵循以下流程：
1. **展示 Diff**: 运行 `git diff --staged` 并将结果展示给用户。
2. **请求确认**: 明确询问用户 "是否确认提交以上更改？(Yes/No)"。
3. **等待指令**: 只有在用户明确回复确认后，方可执行 commit 命令。

## 提交信息规范
- 格式: `<type>(<scope>): <subject>`
- Type 包括但不限于: feat, fix, docs, style, refactor, test, chore.
- 语言: 与代码库主要语言或用户指令语言保持一致（中文/英文）。