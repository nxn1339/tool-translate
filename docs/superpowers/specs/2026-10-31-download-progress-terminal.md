# Feature Specification: Step 1 Download Progress & Live Terminal Console

- **Feature Name:** Download Progress Calibration & Live Terminal Console (Chuẩn hóa % Tải Video và Tích hợp Terminal Giám Sát Tiến Trình)
- **Status:** In Progress
- **Created Date:** 2026-10-31
- **Scope:** Full-stack (Backend yt-dlp & FFmpeg logging/progress hook, FastAPI status payload, Frontend interactive collapsible Terminal & smooth progress UI)

---

## 1. Vấn Đề Hiện Tại & Yêu Cầu (Requirements)

### 1.1. Lỗi & Bất Cập của Tiến Độ % Bước 1:
- `yt-dlp` thường tải luồng Video trước (0% -> 100%), sau đó tiếp tục tải luồng Audio riêng biệt (0% -> 100%). Điều này làm thanh % bị nhảy thụt lùi (từ ~95% tụt về lại 5%), gây hoang mang cho người dùng.
- Sau khi tải xong, quá trình FFmpeg tách âm thanh 16kHz WAV diễn ra nhưng không có cập nhật tiến độ, thanh progress bị đứng đơ trước khi đột ngột nhảy lên 100%.
- Regex bóc tách `_percent_str` trong `downloader.py` dễ gặp lỗi ký tự ANSI escape.

### 1.2. Mục Tiêu Cải Tiến %:
Phân bổ 3 giai đoạn mượt mà, không bao giờ nhảy lùi:
1. **Giai đoạn 1 (5% - 75%):** Tải luồng Video chất lượng cao từ URL.
2. **Giai đoạn 2 (75% - 90%):** Tải luồng Audio đi kèm (nếu tách rời) hoặc gộp luồng.
3. **Giai đoạn 3 (90% - 99%):** FFmpeg trích xuất âm thanh chuẩn 16kHz WAV phục vụ Whisper / OCR.
4. **100%:** Hoàn tất, video sẵn sàng nạp lên canvas và chuyển bước 2.

### 1.3. Terminal Giám Sát Tiến Trình (Live Terminal Console):
- **Vị trí:** Đặt ngay bên dưới thanh tiến trình `step1-progress-box` trong Bước 1.
- **Thiết kế:**
  - Giao diện Dark Console hiện đại (`#0f172a`, font monospace, viền bo tròn, badge trạng thái `>_ Terminal`).
  - Thanh toolbar mini có nút: **Thu gọn/Mở rộng (Collapse/Expand)**, **Xóa log (Clear)**, nút **Sao chép log (Copy)**.
  - Tự động cuộn xuống dòng mới nhất (Auto-scroll to bottom), hỗ trợ tạm dừng cuộn nếu người dùng chủ động lăn chuột lên trên.
  - Các dòng log được gắn timestamp (`[HH:MM:SS]`) và phân loại màu sắc (INFO = cyan/white, WARN = yellow, SUCCESS = green, ERROR = red).
- **Kiến trúc mở rộng:**
  - Dữ liệu log được lưu trong `projects_db[project_id]["logs"]` dạng danh sách.
  - Endpoint `/api/project/{project_id}/status` trả về `logs: List[str]`.
  - Có thể dễ dàng tái sử dụng cho Bước 2 (OCR/Whisper) và Bước 4 (Render FFmpeg).

---

## 2. API Contract & Data Model

### Cập nhật Endpoint `/api/project/{project_id}/status`:
Response JSON bổ sung:
```json
{
  "status": "downloading",
  "progress": 45,
  "message": "Đang tải luồng video (58.2%)...",
  "logs": [
    "[15:15:02] [INFO] Bắt đầu kết nối URL: https://...",
    "[15:15:03] [yt-dlp] Đang trích xuất thông tin video...",
    "[15:15:05] [Download] 58.2% | Đã tải: 32.4MB / 55.6MB | Tốc độ: 4.8MB/s | ETA: 00:05",
    "[15:15:12] [FFmpeg] Bắt đầu trích xuất luồng âm thanh 16kHz WAV..."
  ],
  "download_meta": {
    "speed": "4.8MB/s",
    "eta": "00:05",
    "downloaded_bytes": 34000000,
    "total_bytes": 58300000
  }
}
```

---

## 3. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
- [ ] Tiến độ % tải video tăng tuần tự từ 5% -> 100%, không bị reset hay giật lùi về 0%.
- [ ] Giai đoạn FFmpeg trích xuất âm thanh có tiến độ 90% - 99% và hiển thị thông báo rõ ràng.
- [ ] Terminal xuất hiện ngay dưới thanh progress Bước 1 với giao diện console tối màu, hiển thị chi tiết tốc độ tải, dung lượng, ETA và log thời gian thực.
- [ ] Có nút Thu gọn / Mở rộng Terminal hoạt động trơn tru.
- [ ] Log tự động cuộn xuống dưới cùng khi có dòng mới.
- [ ] Code sạch, không ảnh hưởng các chức năng tải Bilibili / YouTube hiện hành.

