---
name: github-pr-link-generator
description: Use when generating a pre-filled 1-click GitHub Pull Request URL or creating release/sync PR links between branches without GitHub CLI or API tokens.
---

# GitHub PR Link Generator

## Overview

Tự động sinh đường link **1-Click Pull Request** trên GitHub với đầy đủ nhánh đích (`base`), nhánh nguồn (`head`), tiêu đề (`title`) và nội dung mô tả Markdown (`body`) được điền sẵn 100%.

Giúp kỹ sư, PM, QA tạo và chia sẻ PR phát hành (Release PR) hoặc PR tính năng (Feature PR) tức thì mà không cần cài đặt GitHub CLI (`gh`), không cần Personal Access Token (`GITHUB_TOKEN`), và không cần copy/paste thủ công từng trường trên trình duyệt.

## When to Use

- Cần tạo Release PR đồng bộ nhánh (ví dụ: `develop` ➔ `main`).
- Cần tạo Feature PR gộp nhánh tính năng vào `develop`.
- Môi trường làm việc không có hoặc không thể cài `gh` CLI hay API Token (như máy dev Windows, CI runner, hoặc máy khách).
- Cần chia sẻ link tạo PR chuẩn mẫu cho thành viên khác trong team chỉ cần click và duyệt.

## Quick Reference

| Nhu cầu | Lệnh thực thi |
|---|---|
| **Sync develop ➔ main (Release PR)** | `pwsh scripts/generate-pr-link.ps1 -BaseBranch main -HeadBranch develop` |
| **Mở trực tiếp trên trình duyệt** | `pwsh scripts/generate-pr-link.ps1 -BaseBranch main -HeadBranch develop -OpenInBrowser` |
| **Feature PR vào develop** | `pwsh scripts/generate-pr-link.ps1 -BaseBranch develop -HeadBranch <feature-branch>` |
| **Dành cho macOS / Linux (Bash)** | `./scripts/generate-pr-link.sh --base main --head develop --open` |
| **Dùng file Markdown có sẵn** | `pwsh scripts/generate-pr-link.ps1 -BodyFile path/to/pr-body.md` |

## Core Mechanism

GitHub hỗ trợ tạo Pull Request qua query parameters của trang Compare:

```text
https://github.com/{OWNER}/{REPO}/compare/{BASE}...{HEAD}?expand=1&title={ENCODED_TITLE}&body={ENCODED_BODY}
```

- `expand=1`: Mở ngay form tạo Pull Request thay vì chỉ xem diff so sánh.
- `title`: Chuỗi URL-encoded của tiêu đề PR.
- `body`: Chuỗi URL-encoded của nội dung Markdown (hỗ trợ checklist, tiêu đề `##`, bảng biểu).

## Script Usage

Thư mục script nằm tại:
- PowerShell: `.agents/skills/github-pr-link-generator/scripts/generate-pr-link.ps1`
- Bash: `.agents/skills/github-pr-link-generator/scripts/generate-pr-link.sh`

### 1. Windows (PowerShell)

```powershell
# Chạy từ thư mục bất kỳ trong dự án
& ".agents/skills/github-pr-link-generator/scripts/generate-pr-link.ps1" `
    -RepoDir "f:/SmileProject/WishListProject/Src/smile-wishlist-app" `
    -BaseBranch "main" `
    -HeadBranch "develop" `
    -OpenInBrowser
```

### 2. macOS / Linux (Bash)

```bash
chmod +x .agents/skills/github-pr-link-generator/scripts/generate-pr-link.sh
.agents/skills/github-pr-link-generator/scripts/generate-pr-link.sh \
    --dir "../smile-wishlist-app" \
    --base "main" \
    --head "develop" \
    --open
```

## Common Mistakes

| Sai lầm | Hậu quả | Cách xử lý đúng |
|---|---|---|
| Không URL-encode ký tự tiếng Việt hoặc ký tự đặc biệt (`#`, `&`, `?`, `\n`) | URL bị gãy, nội dung bị mất đoạn trên GitHub | Sử dụng `[System.Uri]::EscapeDataString()` (PowerShell) hoặc `urllib.parse.quote()` (Python) |
| Nhầm thứ tự `base` và `head` | Tạo PR ngược chiều (ví dụ merge `main` vào `develop`) | Luôn ghi nhớ: URL là `.../compare/{BASE}...{HEAD}` (`BASE` là nhánh đích nhận code) |
| Thiếu `expand=1` | Trình duyệt chỉ dừng lại ở màn hình so sánh diff, không mở sẵn form PR | Bắt buộc kèm tham số `expand=1` trong query string |
