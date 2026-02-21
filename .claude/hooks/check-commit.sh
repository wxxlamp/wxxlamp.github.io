#!/bin/bash

# 读取 Claude Code 传入的标准输入（包含工具调用信息）
INPUT=$(cat)

# 检查是否是 git commit 命令
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null)

# 如果不是 git commit 命令，直接放行
if ! echo "$COMMAND" | grep -qE '^git commit'; then
  exit 0
fi

# 是 git commit 命令，展示 diff 并要求确认
echo "=========================================" >&2
echo "📋 Claude Code 即将执行: $COMMAND" >&2
echo "=========================================" >&2
git diff --cached --stat >&2
echo "" >&2
git diff --cached >&2
echo "=========================================" >&2

# 等待用户确认（从真实终端读取）
exec < /dev/tty
read -p "✅ 是否允许 Claude Code 执行此提交？(y/N): " confirm <&1 >&2

case "$confirm" in
  y|Y)
    echo "✅ 已允许" >&2
    exit 0
    ;;
  *)
    # 输出 JSON 阻止执行
    echo '{"decision": "block", "reason": "用户拒绝了此次提交"}'
    exit 0
    ;;
esac
