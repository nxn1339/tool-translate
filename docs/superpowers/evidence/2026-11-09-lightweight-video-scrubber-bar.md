# Bằng Chứng Nghiệm Thu: Thanh Thời Gian Tua Video Siêu Mượt (Lightweight Video Scrubber Bar)

## 1. Mục Tiêu Đã Thực Hiện
- [x] Bổ sung thanh điều khiển thời gian `#video-scrubber-card` ngay dưới khung video preview.
- [x] Tách rời hoàn toàn khỏi canvas video, giải quyết triệt để vấn đề bounding box `.bbox` (vùng che / sub) đè lên thanh điều khiển gốc.
- [x] Thiết kế UI thuần CSS/JS dạng Range Slider nhẹ, không tạo DOM node dư thừa, giải phóng 100% nguy cơ lag giật.
- [x] Tích hợp bộ nút điều khiển:
  - Play/Pause (kèm icon đồng bộ theo trạng thái video).
  - Tua lùi 5s (`-5s`).
  - Tua tới 5s (`+5s`).
  - Nhảy câu phụ đề trước (`Câu trước`).
  - Nhảy câu phụ đề sau (`Câu sau`).
- [x] Hỗ trợ phím tắt tiện lợi:
  - Phím `Space`: Bật / Tắt phát video.
  - Phím `Mũi tên Trái (←)`: Tua lùi 5 giây.
  - Phím `Mũi tên Phải (→)`: Tua tới 5 giây.
- [x] Tích hợp thanh kéo tua trực quan (range scrubber) với track fill màu gradient tím-xanh và đồng hồ `00:00.0 / 00:00.0`.
- [x] Đồng bộ âm thanh thuyết minh (`syncDubbingAudioSeek`), phụ đề preview và vị trí câu đang chọn trong bảng phụ đề.

## 2. Chi Tiết Thay Đổi
- **`app/static/index.html`**:
  - Thêm thẻ container `#video-scrubber-card` với các nút điều khiển, thanh slider và timecode display.
  - Cập nhật phiên bản asset lên `v=53` để tránh cache trình duyệt.
- **`app/static/style.css`**:
  - Khai báo CSS cho `.video-scrubber-card`, `.scrubber-btn-group`, `.btn-scrub-action`, `.video-seek-slider`, `.scrubber-track-fill`, `.scrubber-timecode-box`.
- **`app/static/app.js`**:
  - Thêm bộ controller `initVideoScrubber` / `updateScrubberUI()`.
  - Kết nối các sự kiện `input`, `change`, `pointerdown`, `pointerup` trên slider.
  - Kết nối các sự kiện của `previewVideoElement`: `timeupdate`, `seeked`, `loadedmetadata`, `play`, `pause`, `ended`.
  - Thêm phím tắt `ArrowLeft` và `ArrowRight` vào trình lắng nghe `keydown`.

