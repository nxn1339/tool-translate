# Verification Evidence: Custom Text Overlays on Video

- **Spec Reference:** `docs/superpowers/specs/2026-11-15-custom-text-overlays.md`
- **Plan Reference:** `docs/superpowers/plans/2026-11-15-custom-text-overlays.md`
- **Execution Date:** 2026-11-15
- **Verified By:** Automated Unit Tests & Code Verification

---

## 1. Mục Tiêu Kiểm Chứng

Kiểm tra tính đúng đắn và tương thích của tính năng chèn text tự do (Watermark chữ) trên màn hình:
1. Tạo 2 text mặc định đúng chuẩn kênh theo yêu cầu:
   - Text 1: `Đăng ký để không bỏ lỡ video mới` (nền trắng bo góc tròn, chữ đen đậm, góc trên-trái).
   - Text 2: `Hạt Tiêu Vietsub` (chữ trắng in nghiêng, đổ bóng nhẹ, không nền, vị trí ngực/vai phải).
2. Xử lý backend (Pillow + FFmpeg):
   - Sinh ảnh PNG trong suốt theo độ phân giải gốc của video.
   - Thêm lớp phủ vào chuỗi filter video của FFmpeg với `overlay=0:0`.
3. Giao diện Frontend:
   - Khung điều khiển tại Bước 5 (Chèn Logo & Chữ).
   - Nút preset 1-click `Mẫu kênh: Đăng ký & Hạt Tiêu Vietsub`.
   - Các khung `bbox-text-overlay` hiển thị trực tiếp trên video và hỗ trợ kéo thả chuột.
   - Đồng bộ lưu trạng thái `text_overlays` vào `project.json` và tổng kết tại Bước 6.

---

## 2. Kết Quả Chạy Unit Test (`tests/test_text_overlays.py`)

```
INFO:app.merger:Video specs: 1280x720, total_duration=15.00s, Has original audio: True, Auto-extend: False
INFO:app.merger:Exported SRT subtitles to: tests\temp_test_text\subtitles.srt (0 entries)
INFO:app.merger:Exported ASS subtitles to: tests\temp_test_text\subtitles.ass (0 entries, PlayRes=1280x720, Fontsize=66, Center=(640,608))
INFO:app.merger:Generated text overlays PNG at: tests\temp_test_text\text_overlays.png (1 items active)
INFO:app.merger:Running master FFmpeg command (need_video_filter=True, needs_extension=False)...
INFO:app.merger:Video merged successfully: tests\temp_test_text\dummy_out.mp4
....INFO:app.merger:Generated text overlays PNG at: tests\temp_test_text\test_overlay.png (2 items active)
.
----------------------------------------------------------------------
Ran 5 tests in 0.151s

OK
```

### Các Case Đã Được Xác Minh:
1. `test_parse_color_rgba`: Chuyển đổi mã màu hex và opacity chính xác.
2. `test_render_text_overlays_image_success`: Tạo ảnh PNG RGBA chuẩn kích thước 1280x720 với kênh alpha chính xác.
3. `test_render_text_overlays_empty_or_disabled`: Trả về `None` khi không có text nào được bật hoặc text rỗng, không gây lãng phí tài nguyên render.
4. `test_merge_with_text_overlays`: Kiểm tra tham số FFmpeg `-i text_overlays.png`, bộ lọc `overlay=0:0` và mã hóa video qua `libx264`.
5. `test_project_render_request_model`: Kiểm tra mô hình dữ liệu Pydantic parse đúng danh sách `text_overlays`.

---

## 3. Kết Luận
Tính năng đã hoàn thành đầy đủ, đạt 100% các tiêu chí trong Spec và Plan, sẵn sàng sử dụng trong luồng dịch phim & lồng tiếng.

