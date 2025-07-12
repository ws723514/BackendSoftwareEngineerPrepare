# scripts/tag_version.ps1
# 版本标记自动化脚本 (PowerShell版本)

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Write-Host "🚀 开始创建版本 $Version..." -ForegroundColor Green

# 检查是否有未提交的更改
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "📦 发现未提交的更改，正在添加..." -ForegroundColor Yellow
    git add .
    git commit -m "release: $Version - $Message"
} else {
    Write-Host "✅ 工作目录干净，无需提交" -ForegroundColor Green
}

# 创建版本标签
Write-Host "🏷️  创建版本标签..." -ForegroundColor Cyan
git tag -a $Version -m "$Version`: $Message"

# 推送到远程仓库
Write-Host "📤 推送到远程仓库..." -ForegroundColor Blue
git push origin main
git push origin $Version

Write-Host "✅ 版本 $Version 已成功创建并推送" -ForegroundColor Green
Write-Host "🔗 查看版本信息: git show $Version" -ForegroundColor Magenta 