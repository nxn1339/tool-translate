#!/usr/bin/env bash
# ==============================================================================
# 1-Click GitHub Pull Request Link Generator (macOS / Linux)
# ==============================================================================

set -euo pipefail

BASE_BRANCH="main"
HEAD_BRANCH="develop"
TITLE=""
BODY=""
BODY_FILE=""
REPO=""
REPO_DIR="."
OPEN_BROWSER=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base|-b)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --head|-h)
      HEAD_BRANCH="$2"
      shift 2
      ;;
    --title|-t)
      TITLE="$2"
      shift 2
      ;;
    --body)
      BODY="$2"
      shift 2
      ;;
    --body-file|-f)
      BODY_FILE="$2"
      shift 2
      ;;
    --repo|-r)
      REPO="$2"
      shift 2
      ;;
    --dir|-d)
      REPO_DIR="$2"
      shift 2
      ;;
    --open|-o)
      OPEN_BROWSER=1
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# 1. Tự động tìm Repo nếu chưa có
if [ -z "$REPO" ]; then
  ORIGIN_URL="$(git -C "$REPO_DIR" remote get-url origin 2>/dev/null || echo "")"
  if [[ "$ORIGIN_URL" =~ github\.com[:/]([^/]+/[^/.]+)(\.git)?$ ]]; then
    REPO="${BASH_REMATCH[1]}"
  elif [[ "$ORIGIN_URL" =~ github-[^:/]+[:/]([^/]+/[^/.]+)(\.git)?$ ]]; then
    REPO="${BASH_REMATCH[1]}"
  else
    REPO="Smile-Software/smile-wishlist-app"
  fi
fi

REPO="${REPO%.git}"

# 2. Tự động sinh Title & Body nếu rỗng
if [ -z "$TITLE" ]; then
  TITLE="chore(release): sync $HEAD_BRANCH into $BASE_BRANCH"
fi

if [ -n "$BODY_FILE" ] && [ -f "$BODY_FILE" ]; then
  BODY="$(cat "$BODY_FILE")"
elif [ -z "$BODY" ]; then
  COMMITS="$(git -C "$REPO_DIR" log "${BASE_BRANCH}..${HEAD_BRANCH}" --no-merges -n 15 --pretty=format:"- %s" 2>/dev/null || echo "")"
  MERGES="$(git -C "$REPO_DIR" log "${BASE_BRANCH}..${HEAD_BRANCH}" --merges -n 10 --pretty=format:"- %s" 2>/dev/null || echo "")"

  BODY="## 📌 Tóm tắt (Summary)
Đồng bộ mã nguồn từ nhánh \`$HEAD_BRANCH\` sang nhánh \`$BASE_BRANCH\`.

---

## 🚀 Các thay đổi chính (Key Changes)
${COMMITS:-"- Cập nhật các tính năng và bản sửa lỗi mới nhất từ nhánh $HEAD_BRANCH."}"

  if [ -n "$MERGES" ]; then
    BODY="${BODY}

### Các PR đã gộp (Merged Pull Requests)
${MERGES}"
  fi

  BODY="${BODY}

---

## 🔍 Checklist Kiểm thử & Triển khai
- [x] Đã kiểm tra tính tương thích và unit tests.
- [ ] Kiểm tra migration database (nếu có thay đổi schema).
- [ ] Kiểm tra biến môi trường và cấu hình liên quan."
fi

# 3. URL Encode Title & Body
url_encode() {
  local string="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.stdin.read()))" <<< "$string"
  elif command -v perl >/dev/null 2>&1; then
    perl -MURI::Escape -e 'print uri_escape(<STDIN>)' <<< "$string"
  else
    # Fallback cơ bản
    echo -n "$string" | xargs -0 node -e 'console.log(encodeURIComponent(process.argv[1]))' 2>/dev/null || echo "$string"
  fi
}

ENCODED_TITLE="$(url_encode "$TITLE" | tr -d '\r\n')"
ENCODED_BODY="$(url_encode "$BODY" | tr -d '\r\n')"

PR_URL="https://github.com/${REPO}/compare/${BASE_BRANCH}...${HEAD_BRANCH}?expand=1&title=${ENCODED_TITLE}&body=${ENCODED_BODY}"

echo ""
echo "================================================================================"
echo "🔗 ĐƯỜNG LINK 1-CLICK TẠO GITHUB PULL REQUEST:"
echo "================================================================================"
echo "$PR_URL"
echo "================================================================================"
echo "👉 Copy link trên dán vào trình duyệt hoặc bấm trực tiếp để tạo PR tự động!"
echo ""

if [ "$OPEN_BROWSER" -eq 1 ]; then
  echo "🌐 Đang mở trình duyệt..."
  if command -v open >/dev/null 2>&1; then
    open "$PR_URL"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$PR_URL"
  fi
fi
