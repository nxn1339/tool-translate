# Kế Hoạch Triển Khai: Thanh Thời Gian Tua Video Siêu Mượt (Lightweight Video Scrubber Bar)

## Kế Hoạch Từng Bước

### Bước 1: Bổ Sung HTML Thanh Thời Gian Vào `app/static/index.html`
- Thêm container `#video-scrubber-card` ngay sau `.canvas-video-wrapper`.
- Cấu trúc:
  - Cụm nút phát lại: `#btn-scrub-play`, `#btn-scrub-back5`, `#btn-scrub-fwd5`.
  - Cụm nhảy câu sub: `#btn-scrub-prev-sub`, `#btn-scrub-next-sub`.
  - Thanh trượt: `<input type="range" id="video-seek-slider" ...>` kèm `#scrubber-track-fill`.
  - Khối thời gian: `#scrub-current-time` / `#scrub-total-time`.

### Bước 2: Thiết Kế Giao Diện Bằng CSS Trong `app/static/style.css`
- Style dark-mode chuyên nghiệp, bo cong mềm mại, đồng bộ với giao diện Siêu Tool.
- Tùy biến thanh `<input type="range">`:
  - Ẩn track mặc định của trình duyệt (`-webkit-appearance: none`).
  - Thumb tròn gradient có viền phát sáng khi hover/active.
  - Track fill đổi màu theo phần trăm đã phát.
  - Nút bấm có hiệu ứng hover mượt mà và tooltip rõ ràng.

### Bước 3: Viết Logic Điều Khiển Trong `app/static/app.js`
- Khai báo các phần tử DOM của scrubber bar.
- Viết hàm `initVideoScrubber()`:
  - Bắt sự kiện `input` trên `#video-seek-slider` để tua thời gian tức thời.
  - Bắt sự kiện `change` trên `#video-seek-slider` để đồng bộ âm thanh thuyết minh.
  - Bắt sự kiện click `#btn-scrub-play`: chuyển đổi play/pause của video.
  - Bắt sự kiện click `#btn-scrub-back5` và `#btn-scrub-fwd5`: tua -5s / +5s.
  - Bắt sự kiện click `#btn-scrub-prev-sub` và `#btn-scrub-next-sub`: tìm câu phụ đề liền kề và nhảy đến `seg.start`.
- Kết nối sự kiện của `previewVideoElement`:
  - `timeupdate`: Cập nhật vị trí slider và label thời gian nếu không trong trạng thái kéo.
  - `play` / `pause`: Cập nhật icon nút play/pause.
  - `loadedmetadata`: Cập nhật `max` của slider và tổng thời lượng.

### Bước 4: Kiểm Thử & Ghi Bằng Chứng Nghiệm Thu
- Kiểm tra tính mượt mà khi tua video.
- Kiểm tra sự đồng bộ giữa video, âm thanh lồng tiếng và bảng phụ đề.
- Ghi nhận kết quả vào `docs/superpowers/evidence/2026-11-09-lightweight-video-scrubber-bar.md`.

