# Thiết Kế Chi Tiết: Màn Home Hub Quản Lý Đa Tính Năng ("Siêu Tool của NgatCT")

## 1. Mục Tiêu & Bối Cảnh
Dự án hiện tại là một công cụ monolithic phục vụ luồng dịch phim 5 bước (tải video -> OCR -> dịch AI -> TTS CapCut -> chèn logo/xuất video). Để chuẩn bị mở rộng thêm nhiều tính năng media/AI trong tương lai, hệ thống cần:
1. Đổi tên nhận diện thương hiệu thành **"Siêu Tool của NgatCT"**.
2. Bổ sung màn hình **Trang Chủ (Home Hub)** đóng vai trò trung tâm điều khiển, quản lý và điều hướng các chức năng.
3. Chức năng số 1 khả dụng ngay: **"Dịch Phim & Lồng Tiếng Video"**.
4. Các slot tính năng kế tiếp dạng **"Sắp ra mắt"** (Tách âm thanh/Vocal, Dịch SRT rời, TTS độc lập).
5. Tích hợp trực tiếp danh sách **Dự án gần đây (Recent Projects)** ngay tại Home Hub để người dùng tiếp tục làm việc chỉ với 1 click.
6. Hiển thị trạng thái kết nối AI Engine (Gemini / Groq) và shortcut Cài đặt ngay tại Home Hub.

---

## 2. Kiến Trúc Điều Hướng (SPA View Switching)
- **Không reload trang**: Sử dụng cơ chế View Router dựa trên CSS class / State / Hash URL (`#home` và `#dubber`).
- **Hai view chính trong `index.html`**:
  1. `<div id="home-view" class="view-section">`: Màn Home Hub quản lý chức năng và dự án gần đây.
  2. `<main id="workspace-layout" class="studio-workspace view-section">`: Studio Workspace dịch phim hiện tại.
- **Header chung thông minh**:
  - Logo thương hiệu: **Siêu Tool của NgatCT** (click logo luôn quay về Home).
  - Navigation links:
    - `Trang Chủ` (`btn-nav-home`)
    - `Dịch Phim` (`btn-nav-dubber`)
    - `Cài Đặt API` (`btn-nav-settings` - mở modal cấu hình Groq / Gemini)
  - Phím tắt "← Quay lại Trang Chủ" ngay trên Project Control Bar của màn dịch phim.
- **Lưu trạng thái phiên làm việc**:
  - Ghi nhớ view hiện tại vào URL hash (`#home` hoặc `#dubber`). F5 vẫn giữ nguyên view đang đứng.

---

## 3. Cấu Trúc Giao Diện Màn Home Hub

### 3.1. Hero Section
- Lời chào: **"Siêu Tool của NgatCT"**
- Subtitle: *Trung tâm công cụ AI Media & Tự động hóa đa năng*
- Trạng thái AI Engine hiện tại (Pill badge: Groq / Gemini connected / not configured).

### 3.2. Grid Tính Năng (Feature Launchpad)
Mỗi card có icon phong cách Glassmorphism, badge trạng thái, mô tả tính năng và nút kích hoạt:
1. **Dịch Phim & Lồng Tiếng Video**:
   - Badge: `Khả dụng (Active)`
   - Icon: `fa-film` / `fa-wand-magic-sparkles`
   - Mô tả: Tải video Bilibili/YouTube/Local, OCR sub cứng, dịch văn cảnh Hán-Việt AI (Gemini/Groq), lồng tiếng TTS CapCut, che sub cũ, gắn watermark & xuất MP4.
   - Nút: `Mở Studio` (mở dự án gần nhất hoặc hiện tại) và `Dự Án Mới` (tạo dự án trắng mới và vào studio).
2. **Tách Nhạc & Lọc Giọng (Audio Stem Splitter)**:
   - Badge: `Sắp ra mắt`
   - Icon: `fa-waveform-lines`
   - Mô tả: Tách riêng giọng nói (Vocal) và nhạc nền (BGM) chất lượng cao bằng mô hình AI Demucs.
3. **Dịch Phụ Đề Rời (Standalone Subtitle)**:
   - Badge: `Sắp ra mắt`
   - Icon: `fa-closed-captioning`
   - Mô tả: Tải file SRT/VTT/ASS lên để dịch chuẩn thuật ngữ Hán-Việt, xuất nhanh file sub mới mà không cần render video.
4. **Studio Lồng Tiếng Độc Lập (AI Text-to-Speech)**:
   - Badge: `Sắp ra mắt`
   - Icon: `fa-microphone-lines`
   - Mô tả: Nhập văn bản kịch bản tùy ý, tạo giọng đọc CapCut/Edge-TTS mượt mà, tải file MP3/WAV.

### 3.3. Bảng Dự Án Gần Đây (Recent Projects Section)
- Tự động gọi API `/api/projects` để render danh sách 5-10 dự án gần nhất.
- Mỗi card/row dự án hiển thị:
  - Tên dự án (Click để mở thẳng vào Studio).
  - Badge bước hiện tại (VD: *Bước 3: Dịch Phụ Đề*).
  - Thời gian cập nhật gần nhất.
  - Các nút tác vụ nhanh: `Tiếp tục`, `Đổi tên`, `Xóa` (có dialog xác nhận an toàn).
- Trường hợp chưa có dự án nào: Hiển thị Empty State với nút "Tạo dự án dịch phim đầu tiên".

---

## 4. Danh Sách Tệp Tác Động
1. **`app/static/index.html`**:
   - Cập nhật title và thương hiệu header thành "Siêu Tool của NgatCT".
   - Bổ sung Navigation bar trên Header (Trang Chủ, Dịch Phim, Cài Đặt).
   - Thêm container `<div id="home-view">` chứa Hero, Grid thẻ tính năng, Quick status bar, và Bảng dự án gần đây.
   - Thêm nút "← Trang Chủ" trên project control bar của Studio.
2. **`app/static/style.css`**:
   - Thêm style cho Navigation bar trên Header (active states, hover, glow).
   - Thêm style cho Grid thẻ tính năng (Glassmorphism cards, glowing borders, badge Active vs Coming Soon, nút bấm).
   - Thêm style cho danh sách Recent Projects trên màn Home (layout hiện đại, đồng bộ với dark tech theme hiện tại).
3. **`app/static/app.js`**:
   - Hàm `switchView(viewName)` quản lý ẩn/hiện `#home-view` và `#workspace-layout`, đồng bộ `#hash` trên URL.
   - Hàm `renderHomeRecentProjects()` lấy dữ liệu từ `/api/projects` và render danh sách dự án trực tiếp ra Home.
   - Cập nhật logic khởi động: Mặc định mở Home Hub (`#home`), hoặc mở đúng `#dubber` nếu URL hash yêu cầu.

