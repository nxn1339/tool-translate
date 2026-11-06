# Kế Hoạch Triển Khai: Màn Home Hub Quản Lý Đa Tính Năng ("Siêu Tool của NgatCT")

## Kế Hoạch Theo Từng Bước (Implementation Steps)

### Bước 1: Cập Nhật Cấu Trúc HTML (`app/static/index.html`)
- Thay đổi `<title>` và logo/header text thành **"Siêu Tool của NgatCT"**.
- Chèn Navigation Bar vào `<header>` gồm:
  - Nút `Trang Chủ` (`#btn-nav-home`)
  - Nút `Dịch Phim` (`#btn-nav-dubber`)
  - Nút `Cài Đặt API` (`#btn-nav-settings`)
- Thêm section `#home-view` nằm song song với `#workspace-layout`:
  - **Hero Section**: Chào mừng, tóm tắt hệ thống, trạng thái AI Engine.
  - **Feature Grid**: Thẻ 1 "Dịch Phim & Lồng Tiếng" (Active, 2 nút: Mở Studio & Tạo Dự Án Mới), Thẻ 2 "Tách Nhạc & Lọc Giọng" (Coming soon), Thẻ 3 "Dịch Phụ Đề Rời" (Coming soon), Thẻ 4 "Studio Lồng Tiếng Độc Lập" (Coming soon).
  - **Recent Projects Section**: Container `#home-recent-projects-list` render các project gần đây kèm nút Xóa, Mở, Tạo mới.
- Thêm nút `← Trang Chủ` (`#btn-back-to-home`) vào thanh `#project-bar` ở chế độ Studio.

### Bước 2: Bổ Sung Định Dạng Giao Diện (`app/static/style.css`)
- Style cho `.header-nav`: Flex layout, tabs dạng capsule hiện đại với hiệu ứng gradient/glow khi active.
- Style cho `#home-view`: Bố cục container thoáng đãng, cân xứng.
- Style cho `.feature-grid` & `.feature-card`:
  - Card bo tròn, nền kính tối (Dark Glassmorphism), border viền sáng nhẹ, hover glow hiệu ứng nổi khối.
  - Badge trạng thái: `.badge-active` (xanh neon/tím phát sáng), `.badge-coming-soon` (xám khói tinh tế).
  - Khối nút hành động trong card.
- Style cho `.recent-projects-card`:
  - Bảng hoặc danh sách thẻ dự án gần đây: hiển thị tên dự án, thời gian, thẻ tiến độ bước 1-6.
  - Responsive mượt mà trên cả màn hình lớn và laptop nhỏ.

### Bước 3: Xử Lý Logic JavaScript (`app/static/app.js`)
- Thêm hàm điều hướng `switchView(viewName, pushHistory = true)`:
  - `viewName === 'home'`: Hiển thị `#home-view`, ẩn `#workspace-layout`, kích hoạt tab Home, gọi `renderHomeRecentProjects()`.
  - `viewName === 'dubber'`: Hiển thị `#workspace-layout`, ẩn `#home-view`, kích hoạt tab Dịch Phim.
  - Đồng bộ `window.location.hash` (`#home` vs `#dubber`) và bắt sự kiện `window.onhashchange`.
- Thêm hàm `renderHomeRecentProjects()`:
  - Lấy danh sách từ `/api/projects`.
  - Render thẻ dự án gần đây với đầy đủ thông tin: Tên, Bước hiện tại (lấy từ `STEP_NAMES`), thời gian cập nhật.
  - Xử lý sự kiện click mở dự án -> nạp dữ liệu qua `openProject(id)` -> tự động `switchView('dubber')`.
  - Xử lý sự kiện xóa dự án trực tiếp từ Home (sử dụng modal xác nhận `showConfirmDialog`).
- Cập nhật logic khởi chạy `initStudioSession()`:
  - Mặc định đọc URL hash: nếu là `#dubber` thì mở Studio; nếu không có hoặc là `#home` thì mở màn Home Hub.
  - Nút "Dự Án Mới" tại thẻ Home: gọi `createNewProject(true)` rồi tự động `switchView('dubber')`.
  - Nút Logo trên header: click chuyển về Home view.

### Bước 4: Kiểm Thử & Xác Nhận (Verification)
1. Kiểm tra chuyển đổi qua lại giữa Home và Studio:
   - Click "Trang Chủ" -> màn Home hiện ra, Studio ẩn.
   - Click "Dịch Phim" -> Studio hiện ra, trạng thái project giữ nguyên vẹn.
   - Nhấn Back / Forward trên trình duyệt -> hash chuyển đổi đúng view.
2. Kiểm tra thao tác dự án từ màn Home:
   - Dự án hiển thị đầy đủ tên và bước hiện tại.
   - Nhấp vào dự án -> mở đúng project và chuyển sang Studio.
   - Bấm "Dự Án Mới" từ Home -> tạo dự án trắng mới và chuyển vào Studio.
   - Bấm nút "Xóa" dự án từ Home -> popup xác nhận xuất hiện, đồng ý -> xóa thành công và cập nhật lại danh sách.
3. Kiểm tra tính năng Dịch Phim gốc:
   - Các bước 1 đến 6 vẫn hoạt động 100% trơn tru, không bị ảnh hưởng bởi layout Home.

