#!/bin/bash
# scripts/tag_version.sh
# 版本标记自动化脚本

VERSION=$1
MESSAGE=$2

if [ -z "$VERSION" ] || [ -z "$MESSAGE" ]; then
    echo "❌ 用法: ./tag_version.sh v1.1.0 '版本描述'"
    echo "📝 示例: ./tag_version.sh v1.1.0 '添加服务器流式推送功能'"
    exit 1
fi

echo "🚀 开始创建版本 $VERSION..."

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📦 发现未提交的更改，正在添加..."
    git add .
    git commit -m "release: $VERSION - $MESSAGE"
else
    echo "✅ 工作目录干净，无需提交"
fi

# 创建版本标签
echo "🏷️  创建版本标签..."
git tag -a $VERSION -m "$VERSION: $MESSAGE"

# 推送到远程仓库
echo "📤 推送到远程仓库..."
git push origin main
git push origin $VERSION

echo "✅ 版本 $VERSION 已成功创建并推送"
echo "🔗 查看版本信息: git show $VERSION" 