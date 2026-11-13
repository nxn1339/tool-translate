# Kế Hoạch: Đồng Bộ Kích Thước Vùng Che Mờ Theo Khung Phụ Đề Hiển Thị (Green Box)

## 1. Mục Tiêu
- Khi người dùng kéo dãn, di chuyển hoặc thay đổi kích thước Khung Xanh (Khung hiển thị phụ đề tiếng Việt `sub_box`), kích thước và vị trí của vùng che mờ (`mask_box`) phải tự động đồng bộ theo 100%.
- Đảm bảo khi xuất video hoàn chỉnh bằng FFmpeg, vệt che mờ (blur / solid) luôn ôm đúng kích thước và tọa độ của khung phụ đề đã được kéo dãn trên giao diện, không bị lệch hoặc giữ kích thước cũ.

## 2. Các Bước Triển Khai
### Bước 1: Cập Nhật Frontend (`app/static/app.js`)
- Trong `setupDragAndResize(bboxSub, ...)`: Đồng bộ `maskBoxCoords = { ...newCoords }` cả trong quá trình kéo thả (`onSync`) lẫn khi kết thúc kéo thả (`setCoords`).
- Trong `onMouseUp` của `setupDragAndResize`: Tự động gọi `triggerDebouncedAutoSave` để lưu lại tọa độ mới sau khi người dùng thả chuột.
- Đồng bộ cả 2 chiều trong các nút preset (Căn đáy, Căn đỉnh, Reset).

### Bước 2: Cập Nhật Backend Renderer (`app/merger.py`)
- Trong `merge_audio_segments_to_video()`: Khi tạo filter che mờ (`boxblur` / `solid`), ưu tiên lấy tọa độ `(x, y, w, h)` từ `sub_box` nếu có, đảm bảo video render luôn dùng đúng kích thước khung phụ đề mới nhất mà người dùng đã kéo dãn.

### Bước 3: Kiểm Thử & Nghiệm Thu
- Kiểm tra tính hợp lệ cú pháp của `app/merger.py` (`py_compile`).
- Ghi nhận bằng chứng nghiệm thu tại `docs/superpowers/evidence/2026-11-13-sync-mask-box-to-subtitle-box.md`.

