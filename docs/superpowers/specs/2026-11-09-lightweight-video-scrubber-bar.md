# Thiết Kế Chi Tiết: Thanh Thời Gian Tua Video Siêu Mượt (Lightweight Video Scrubber Bar)

## 1. Bối Cảnh & Vấn Đề
- **Vấn đề 1:** Bounding box của vùng che và sub (`.bbox-mask`, `.bbox-sub`) nằm ở đáy khung video (`top: 78%`), đè lên thanh điều khiển gốc của trình duyệt khiến người dùng không thể bấm tua video được.
- **Vấn đề 2:** Bộ timeline cũ (`#timeline-editor-card`) bị ẩn (`d-none`) vì việc tạo hàng ngàn thẻ DOM cho từng câu sub gây lag giật trình duyệt.
- **Yêu cầu cốt lõi:** Thêm thanh thời gian tua được thời gian, trực quan, nhạy, **tuyệt đối không làm lag app**.

---

## 2. Giải Pháp Kỹ Thuật
1. **Vị trí hiển thị:** Đặt ngay dưới `.canvas-video-wrapper` và trên các khối chức năng. Tách biệt hoàn toàn khỏi khung video nên không bao giờ bị bounding box che khuất.
2. **Kiến trúc UI siêu nhẹ (Zero Lag):**
   - Sử dụng 1 thẻ `<input type="range">` duy nhất được custom style bằng CSS hiện đại (Cyberpunk / Studio dark mode).
   - Thanh tiến trình lấp đầy (progress fill) dùng gradient tím-hồng bắt mắt.
   - Hiển thị timecode: `Thời gian hiện tại / Tổng thời lượng` (vd: `00:15.2 / 03:45.0`).
   - Cụm nút thao tác nhanh:
     - Nút Play/Pause (kèm icon đồng bộ theo trạng thái phát).
     - Nút Tua lùi 5 giây (`-5s`).
     - Nút Tua tới 5 giây (`+5s`).
     - Nút Nhảy câu phụ đề trước / sau (`Câu trước` / `Câu sau`).
3. **Cơ chế đồng bộ thời gian:**
   - Khi kéo rê thanh slider (`input` event): Cập nhật ngay `previewVideoElement.currentTime`, nhãn thời gian, và phụ đề preview mà không cần chờ nhả chuột.
   - Khi nhả chuột (`change` event): Đồng bộ lại âm thanh lồng tiếng (`dubbingAudio`).
   - Khi video tự phát (`timeupdate` event): Nếu người dùng không đang kéo chuột (`!isScrubbing`), cập nhật giá trị slider và thanh fill theo tiến trình video.
   - Khi bấm chuyển câu phụ đề: Video nhảy đến `seg.start`, đồng thời tự động cuộn bảng phụ đề và highlight câu đang chọn.
4. **Tối ưu hiệu năng:**
   - Không sinh thêm bất kỳ DOM node nào trong quá trình phát hay tua.
   - Thao tác tính toán thời gian `O(1)`.
   - Đảm bảo 60fps mượt mà trên mọi video thời lượng dài (vài chục phút đến nhiều tiếng).

