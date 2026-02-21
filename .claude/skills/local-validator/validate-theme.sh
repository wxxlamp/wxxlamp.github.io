#!/bin/bash
set -e

echo "🧹 Cleaning..."
hexo clean

echo "🔨 Generating..."
hexo generate --debug 2>&1 | tee build.log

echo "🔍 Checking for errors..."
if grep -i "error\|fatal" build.log; then
    echo "❌ Build errors found!"
    exit 1
fi

echo "🚀 Starting server..."
hexo server -p 4000 &
SERVER_PID=$!
sleep 3

echo "✅ Server running at http://localhost:4000"
echo "Press Ctrl+C to stop"

# Cleanup on exit
trap "kill $SERVER_PID 2>/dev/null; exit" INT
wait
