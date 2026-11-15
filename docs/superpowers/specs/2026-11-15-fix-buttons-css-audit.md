# Đặc Tả Kỹ Thuật: Điều Tra & Sửa Triệt Để Lỗi CSS Toàn Bộ Các Nút Bấm (Button Audit & Fix)

## 1. Nguyên Nhân Gốc Rễ (Root Cause Analysis)

Từ ảnh chụp màn hình người dùng cung cấp và qua điều tra toàn bộ mã nguồn:

### 1.1. Lỗi chính gây vỡ giao diện nút bộ lọc (`.home-filter-tab`)
- **Bộ nhớ đệm (Browser Cache) do chưa tăng version css**:
  Trong `app/static/index.html` dòng 24, thẻ nạp CSS là `<link rel="stylesheet" href="style.css?v=60">`.
  Khi thêm các class `.home-projects-filter-bar` và `.home-filter-tab` vào cuối file `style.css`, chuỗi phiên bản `?v=60` không được tăng lên. Trình duyệt người dùng giữ lại bản cache cũ của `style.css?v=60` từ phiên làm việc trước đó (bản chưa hề có các class này).
- **Thiếu CSS Reset toàn cục cho thẻ `<button>`**:
  Trong `style.css`, khối reset `* { margin: 0; padding: 0; box-sizing: border-box; }` **hoàn toàn không có reset cho thẻ `button`**.
  Hệ quả: Bất cứ nút nào trong app nếu bị lỗi cache hoặc class chưa khớp sẽ lập tức bị trình duyệt giáng cấp về giao diện mặc định thô sơ (User-Agent Stylesheet): nền trắng xám bóng bẩy Windows cổ điển (`buttonface`), chữ đen xì (`buttontext`), viền beveled 2px nổi gồ ghề (`outset`), góc vuông nhọn hoắt và dính sát vào nhau không có padding/margin — đúng y hệt những gì hiển thị trong ảnh chụp!

### 1.2. Rà soát các nút khác trên toàn bộ App
Qua rà soát 194 thẻ `<button>` và các đoạn HTML sinh động trong `app.js`:
1. **Class thiếu trong `style.css`**:
   - `.btn-subtle`: Đang gán cho các nút `#btn-toggle-terminal-global` (Mở terminal), `#btn-tl-refresh-dub` (Làm mới âm thanh timeline), `#btn-upload-logo` (Chọn ảnh logo) nhưng trong `style.css` chưa hề định nghĩa class này (chỉ có `.btn-subtle-toggle` và `.btn-icon-subtle`).
   - `.collapsible-btn`: Nút `#btn-toggle-cookie` (Bật/tắt Cookie Bilibili) chưa có style trong CSS.
   - `.text-danger`: Nút xóa dự án trên các card gần đây (`.btn-home-del-proj`) có gán class `text-danger` nhưng class này chưa có trong CSS, khiến icon thùng rác không có màu đỏ cảnh báo.
   - `.btn-home-del-proj`: Nút xóa thùng rác trên card gần đây chưa có style chuẩn (kích thước, padding, border-radius, hiệu ứng hover), bị lệch trục và dính cạnh nút "Tiếp Tục".
   - `.btn-collapse`: Class phụ trợ thu gọn terminal chưa được chuẩn hóa.

---

## 2. Giải Pháp Toàn Diện

1. **Thêm CSS Reset toàn cục cho `button`** vào đầu `style.css`:
   ```css
   button {
       font-family: inherit;
       font-size: inherit;
       border: none;
       outline: none;
       background: transparent;
       color: inherit;
       cursor: pointer;
   }
   ```
   *Tác dụng*: Đảm bảo không bao giờ một nút nào trong app bị văng về giao diện trắng xám chữ đen thô kệch của hệ điều hành, kể cả khi CSS con bị trễ tải.

2. **Bổ sung đầy đủ các class nút còn thiếu trong `style.css`**:
   - `.btn-subtle`: Nút phụ tinh gọn (background mờ tối, viền mỏng, bo góc 10px, hover sáng).
   - `.collapsible-btn`: Nút accordion mở rộng/thu gọn (Cookie VIP).
   - `.text-danger`: Màu đỏ cảnh báo `#f87171` kèm hiệu ứng hover đỏ rực.
   - `.btn-home-del-proj`: Nút thùng rác vuông vắn 36x36px, nền đỏ mờ, bo góc 10px, căn chỉnh ngang hàng hoàn hảo với nút "Tiếp Tục".

3. **Cập nhật Cache Buster trong `index.html`**:
   - Đổi `href="style.css?v=60"` thành `href="style.css?v=62"`.
   - Đổi `src="app.js?v=60"` thành `src="app.js?v=62"`.

