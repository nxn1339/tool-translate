# Bằng Chứng Nghiệm Thu (Evidence): Sửa Triệt Để Lỗi CSS Nút & Chuẩn Hóa Button Toàn Ứng Dụng

**Ngày thực hiện:** 15/11/2026  
**Mục tiêu:** Khắc phục triệt để lỗi nút bị văng về giao diện thô sơ (nền trắng chữ đen viền thô), xử lý lỗi cache CSS trình duyệt, bổ sung reset toàn cục và khai báo đầy đủ các class nút còn thiếu trên toàn bộ ứng dụng.

---

## 1. Tóm Tắt Các Thay Đổi Đã Thực Hiện

### 1.1 `app/static/style.css`
1. **Thêm Global `<button>` Reset**:
   ```css
   button {
       font-family: inherit;
       font-size: inherit;
       border: none;
       outline: none;
       background: transparent;
       color: inherit;
       cursor: pointer;
       -webkit-tap-highlight-color: transparent;
   }
   ```
   *Hiệu quả*: Triệt tiêu hoàn toàn nguy cơ bất kỳ thẻ `<button>` nào bị giáng cấp về User-Agent mặc định của OS (nền trắng xám, chữ đen, viền 2px outset).

2. **Gia cố `.home-filter-tab`**:
   - Khai báo rõ ràng font chữ `var(--font-sans)`, bo tròn viên thuốc `border-radius: 9999px`, nền kính tối `rgba(15, 23, 42, 0.65)`, viền mờ `border: 1px solid rgba(255, 255, 255, 0.12)`, padding chuẩn `0.4rem 0.95rem`, hiệu ứng hover và active phát sáng tím-xanh.

3. **Bổ sung các class nút còn thiếu trên toàn app**:
   - `.btn-subtle`: Áp dụng cho nút mở terminal, làm mới âm thanh và tải ảnh logo.
   - `.collapsible-btn`: Áp dụng cho nút mở rộng nhập cookie Bilibili.
   - `.btn-lg`: Nút kích thước lớn cho tác vụ xuất video.
   - `.btn-collapse`: Class phụ trợ thu gọn/mở rộng terminal.
   - `.text-danger` & `.btn-home-del-proj`: Chuẩn hóa nút xóa dự án (kích thước vuông 36x36px, nền đỏ trong mờ, bo góc 10px, căn chỉnh hàng ngang chuẩn xác với nút "Tiếp Tục").

### 1.2 `app/static/index.html`
- Tăng Cache Buster phiên bản CSS: `style.css?v=62`.
- Tăng Cache Buster phiên bản JS: `app.js?v=62`.

---

## 2. Kết Quả Kiểm Thử (Audit & Test Suite)

### 2.1 Kiểm tra đối soát 194 thẻ `<button>` và dynamic JS elements
Đã quét toàn bộ DOM HTML và template literals trong `app.js`:
- **Số lượng class bị thiếu trong `index.html`**: `0` (Tất cả 100% class đều đã được định nghĩa trong `style.css`).
- **Số lượng class bị thiếu trong `app.js`**: `0`.

### 2.2 Bộ kiểm thử tự động (Regression Tests)
- `tests/test_auto_cleanup_projects.py`: **7/7 PASSED**
- `tests/test_unified_projects_and_terminals.py`: **4/4 PASSED**
- **Tổng cộng: 11/11 tests PASSED**.

