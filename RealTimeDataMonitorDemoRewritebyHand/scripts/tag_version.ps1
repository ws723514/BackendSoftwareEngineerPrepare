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

# 验证版本格式（确保使用grpc-前缀）
if (-not $Version.StartsWith("grpc-")) {
    Write-Host "⚠️  建议使用 grpc- 前缀避免与主仓库版本冲突" -ForegroundColor Yellow
    $confirm = Read-Host "是否继续？(y/N)"
    if (($confirm -ne "y") -and ($confirm -ne "Y")) {
        Write-Host "❌ 操作已取消" -ForegroundColor Red
        exit 1
    }
}

# 创建版本标签
Write-Host "🏷️  创建版本标签..." -ForegroundColor Cyan
git tag -a $Version -m "$Version`: $Message"

# 推送到远程仓库
Write-Host "📤 推送到远程仓库..." -ForegroundColor Blue
$currentBranch = git branch --show-current
git push origin $currentBranch
git push origin $Version

Write-Host "✅ 版本 $Version 已成功创建并推送" -ForegroundColor Green
Write-Host "🔗 查看版本信息: git show $Version" -ForegroundColor Magenta 