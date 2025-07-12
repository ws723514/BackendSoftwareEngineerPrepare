# scripts/show_versions.ps1
# 版本查看脚本 (PowerShell版本)

Write-Host "📋 所有版本列表:" -ForegroundColor Cyan
$tags = git tag --list --sort=-version:refname
if ($tags) {
    $tags | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
} else {
    Write-Host "  无版本标签" -ForegroundColor Gray
}

Write-Host "`n📊 版本统计:" -ForegroundColor Cyan
$tagCount = (git tag --list).Count
Write-Host "总版本数: $tagCount" -ForegroundColor White

# 检查是否有标签
if ($tagCount -gt 0) {
    $latestTag = git describe --tags --abbrev=0 2>$null
    if ($latestTag) {
        Write-Host "最新版本: $latestTag" -ForegroundColor Green
    } else {
        Write-Host "最新版本: 无标签" -ForegroundColor Gray
    }
} else {
    Write-Host "最新版本: 无标签" -ForegroundColor Gray
}

$currentBranch = git branch --show-current
Write-Host "当前分支: $currentBranch" -ForegroundColor Magenta

Write-Host "`n🔍 最近5次提交:" -ForegroundColor Cyan
$commits = git log --oneline -5
$commits | ForEach-Object { Write-Host "  $_" -ForegroundColor White }

Write-Host "`n📈 版本发布历史:" -ForegroundColor Cyan
$versionHistory = git log --tags --simplify-by-decoration --pretty="format:%ai %d %s" | Select-Object -First 10
if ($versionHistory) {
    $versionHistory | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} else {
    Write-Host "  无版本发布历史" -ForegroundColor Gray
} 