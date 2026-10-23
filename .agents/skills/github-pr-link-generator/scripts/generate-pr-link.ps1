<#
.SYNOPSIS
    Tạo đường link GitHub 1-Click Pull Request tự động điền sẵn Base, Head, Title và Description.

.DESCRIPTION
    Script này hỗ trợ dev/QA/PM tạo đường link GitHub Pull Request nhanh chóng không cần
    cài đặt GitHub CLI (gh) hay cấu hình GITHUB_TOKEN. Có thể tự động phát hiện repo và
    tóm tắt danh sách commit giữa 2 nhánh.

.PARAMETER BaseBranch
    Nhánh đích (Target/Base), mặc định là 'main'.

.PARAMETER HeadBranch
    Nhánh nguồn (Source/Compare), mặc định là 'develop'.

.PARAMETER Title
    Tiêu đề của Pull Request. Nếu không truyền, script sẽ tự động tạo dựa trên các commit gần nhất.

.PARAMETER Body
    Nội dung mô tả Markdown. Nếu không truyền, script sẽ tự động tổng hợp từ git log.

.PARAMETER BodyFile
    Đường dẫn tới file Markdown chứa nội dung PR (tùy chọn).

.PARAMETER Repo
    Tên repo dạng 'Owner/Repo' (ví dụ 'Smile-Software/smile-wishlist-app').
    Mặc định script sẽ tự lấy từ git remote 'origin'.

.PARAMETER OpenInBrowser
    Bật cờ này để tự động mở đường link trên trình duyệt mặc định.

.EXAMPLE
    .\generate-pr-link.ps1 -BaseBranch main -HeadBranch develop -OpenInBrowser
#>

[CmdletBinding()]
param (
    [string]$BaseBranch = "main",
    [string]$HeadBranch = "develop",
    [string]$Title = "",
    [string]$Body = "",
    [string]$BodyFile = "",
    [string]$Repo = "",
    [string]$RepoDir = ".",
    [switch]$OpenInBrowser
)

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 1. Xác định Repository Owner/Name
if (-not $Repo) {
    try {
        $originUrl = git -C $RepoDir remote get-url origin 2>$null
        if ($originUrl -match "github\.com[:/](.+?)(?:\.git)?$") {
            $Repo = $matches[1]
        } elseif ($originUrl -match "github-[^:/]+[:/](.+?)(?:\.git)?$") {
            $Repo = $matches[1]
        }
    } catch {
        # Bỏ qua nếu lỗi
    }
}

if (-not $Repo) {
    $Repo = "Smile-Software/smile-wishlist-app"
}

$Repo = $Repo -replace "\.git$", ""

# 2. Tự động sinh Title và Body nếu chưa được cung cấp
if (-not $Title) {
    $Title = "chore(release): sync $HeadBranch into $BaseBranch"
}

if ($BodyFile -and (Test-Path $BodyFile)) {
    $Body = Get-Content -Path $BodyFile -Raw -Encoding UTF8
} elseif (-not $Body) {
    $commits = git -C $RepoDir log "$BaseBranch..$HeadBranch" --no-merges -n 15 --pretty=format:"- %s" 2>$null
    $mergeCommits = git -C $RepoDir log "$BaseBranch..$HeadBranch" --merges -n 10 --pretty=format:"- %s" 2>$null

    $BodyBuilder = @()
    $BodyBuilder += "## 📌 Tóm tắt (Summary)"
    $BodyBuilder += "Đồng bộ mã nguồn từ nhánh ``$HeadBranch`` sang nhánh ``$BaseBranch``."
    $BodyBuilder += ""
    $BodyBuilder += "---"
    $BodyBuilder += ""
    $BodyBuilder += "## 🚀 Các thay đổi chính (Key Changes)"
    
    if ($commits) {
        $BodyBuilder += $commits
    } else {
        $BodyBuilder += "- Cập nhật các tính năng và bản sửa lỗi mới nhất từ nhánh $HeadBranch."
    }

    if ($mergeCommits) {
        $BodyBuilder += ""
        $BodyBuilder += "### Các PR đã gộp (Merged Pull Requests)"
        $BodyBuilder += $mergeCommits
    }

    $BodyBuilder += ""
    $BodyBuilder += "---"
    $BodyBuilder += ""
    $BodyBuilder += "## 🔍 Checklist Kiểm thử & Triển khai"
    $BodyBuilder += "- [x] Đã kiểm tra tính tương thích và unit tests."
    $BodyBuilder += "- [ ] Kiểm tra migration database (nếu có thay đổi schema)."
    $BodyBuilder += "- [ ] Kiểm tra biến môi trường và cấu hình liên quan."

    $Body = $BodyBuilder -join "`n"
}

# 3. URL Encode Title & Body
$encodedTitle = [System.Uri]::EscapeDataString($Title)
$encodedBody = [System.Uri]::EscapeDataString($Body)

# 4. Tạo URL GitHub Compare / PR
$prUrl = "https://github.com/$Repo/compare/$BaseBranch...$HeadBranch`?expand=1&title=$encodedTitle&body=$encodedBody"

Write-Output ""
Write-Output "================================================================================"
Write-Output "🔗 ĐƯỜNG LINK 1-CLICK TẠO GITHUB PULL REQUEST:"
Write-Output "================================================================================"
Write-Output $prUrl
Write-Output "================================================================================"
Write-Output "👉 Copy link trên dán vào trình duyệt hoặc bấm trực tiếp để tạo PR tự động!"
Write-Output ""

# 5. Mở trình duyệt nếu được yêu cầu
if ($OpenInBrowser) {
    Write-Output "🌐 Đang mở trình duyệt..."
    Start-Process $prUrl
}