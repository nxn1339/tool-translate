# Kế Hoạch Triển Khai: Sửa Lỗi CSS Nút & Chuẩn Hóa Button Toàn Ứng Dụng

## 1. Danh Sách Tệp Tác Động
1. `app/static/style.css`:
   - Thêm base reset cho thẻ `button`.
   - Bổ sung style cho `.btn-subtle`, `.collapsible-btn`, `.text-danger`, `.btn-home-del-proj`.
   - Gia cố style `.home-filter-tab` (border-radius, padding, badge glow, active state).
2. `app/static/index.html`:
   - Tăng version cache buster lên `v=62` cho cả `style.css` và `app.js`.

---

## 2. Các Bước Triển Khai Chi Tiết

### Bước 1: Thêm Global Button Reset & Missing Classes vào `app/static/style.css`
- Thêm `button` reset ngay sau `* { box-sizing: border-box; }`.
- Khai báo `.btn-subtle` cho các nút tiện ích mở terminal, làm mới audio và chọn logo.
- Khai báo `.collapsible-btn` cho nút mở rộng nhập cookie.
- Khai báo `.text-danger` và `.btn-home-del-proj` cho nút xóa card dự án.
- Tinh chỉnh `.home-filter-tab` và `.home-projects-filter-bar`.

### Bước 2: Tăng Cache Version trong `app/static/index.html`
- Đổi `style.css?v=60` -> `style.css?v=62`.
- Đổi `app.js?v=60` -> `app.js?v=62`.

### Bước 3: Kiểm Thử
- Chạy script kiểm tra rà soát toàn bộ thẻ `<button>` trong HTML và JS để đảm bảo 100% không còn class nút nào bị thiếu trong `style.css`.
- Chạy lại toàn bộ test suite để đảm bảo không ảnh hưởng backend.
- Lưu bằng chứng nghiệm thu vào `docs/superpowers/evidence/2026-11-15-fix-buttons-css-audit.md`.

