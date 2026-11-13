# Bằng Chứng Nghiệm Thu: Đồng Bộ Kích Thước Vùng Che Mờ Theo Khung Phụ Đề Hiển Thị

## 1. Chi Tiết Thay Đổi

### A. Frontend (`app/static/app.js`)
- **`setupDragAndResize` cho `bboxSub` (Khung Xanh phụ đề tiếng Việt)**:
  - Khi người dùng kéo di chuyển hoặc kéo 4 góc để co giãn Khung Xanh, tọa độ `maskBoxCoords` được đồng bộ lập tức bằng `{ ...newCoords }` trong cả hàm `setCoords` lẫn callback `onSync`.
  - Tự động gọi `applyBoxStyles()` để cập nhật vị trí đồng bộ.
  - Khi thả chuột (`onMouseUp`), tự động kích hoạt `triggerDebouncedAutoSave(600)` để lưu ngay tọa độ mới của cả 2 khung lên backend.
- **`setupDragAndResize` cho `bboxMask` (Khung Đỏ)**:
  - Đồng bộ ngược lại cho `subBoxCoords = { ...newCoords }`.
- **Preset buttons (Căn đáy, Căn đỉnh, Reset)**:
  - Đảm bảo gán đồng bộ cả `maskBoxCoords` và `subBoxCoords`, kèm `triggerDebouncedAutoSave(500)`.

### B. Backend (`app/merger.py`)
- Trong `merge_audio_segments_to_video()` (dòng 500-506):
  - Kiểm tra `box_src = sub_box if (sub_box and isinstance(sub_box, dict) and any(k in sub_box for k in ("x", "y", "w", "h"))) else mask_box`.
  - Khi render video bằng FFmpeg filter (`boxblur` hoặc `drawbox`), tọa độ `(x, y, w, h)` của lớp che mờ sẽ ưu tiên lấy chuẩn xác theo Khung Xanh `sub_box` mà người dùng đã kéo dãn trên giao diện.

## 2. Kiểm Tra Kiểm Thử
- **Cú pháp Python**: `python -m py_compile app/merger.py` -> Exit code 0 (thành công).
- **Git Diff**: Đã đối chiếu các dòng thay đổi, không phát sinh xung đột, định dạng chuẩn.

