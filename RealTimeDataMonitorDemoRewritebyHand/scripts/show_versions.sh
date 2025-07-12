#!/bin/bash
# scripts/show_versions.sh
# 版本查看脚本

echo "📋 所有版本列表:"
git tag --list --sort=-version:refname

echo -e "\n📊 版本统计:"
echo "总版本数: $(git tag --list | wc -l)"

# 检查是否有标签
if [ $(git tag --list | wc -l) -gt 0 ]; then
    echo "最新版本: $(git describe --tags --abbrev=0)"
else
    echo "最新版本: 无标签"
fi

echo "当前分支: $(git branch --show-current)"

echo -e "\n🔍 最近5次提交:"
git log --oneline -5

echo -e "\n📈 版本发布历史:"
git log --tags --simplify-by-decoration --pretty="format:%ai %d %s" | head -10 