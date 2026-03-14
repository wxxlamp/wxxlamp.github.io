#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')

# Check if this is a git commit command
if [[ "$cmd" =~ ^git\ commit ]]; then
  # Get staged diff before commit
  diff=$(git diff --cached)

  if [ -n "$diff" ]; then
    # Use Claude to regenerate README.md based on project and staged changes
    claude -p "Read the current README.md and CLAUDE.md of this project. Based on the project structure and the following staged changes, update README.md to reflect the current state. Only modify README.md, do not touch any other files. Staged diff: $diff" --allowedTools 'Read,Write,Glob' 2>/dev/null

    # Stage the updated README.md so it's included in this commit
    git add README.md 2>/dev/null
  fi
fi

# Allow the original command to proceed
echo "{}"
