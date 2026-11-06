# Implementation Plan: Step 1 Download Progress & Live Terminal Console

- **Spec Reference:** `docs/superpowers/specs/2026-10-31-download-progress-terminal.md`
- **Execution Date:** 2026-10-31

---

## Các Bước Triển Khai (Phased Tasks)

### Phase 1: Nâng cấp Backend Download Engine (`app/downloader.py`)
- [ ] Xây dựng class `YtDlpLogger` chuyển tiếp log từ yt-dlp vào callback log.
- [ ] Cải tiến hàm hook `ytdl_hook`:
  - Phân biệt luồng đang tải: `video` hay `audio` dựa vào `info_dict` / filename.
  - Phân bổ trọng số %:
    - Luồng video: Map từ 5% -> 75%
    - Luồng audio: Map từ 75% -> 90%
  - Định dạng thông số tốc độ (`_speed_str`), dung lượng (`_downloaded_bytes_str` / `_total_bytes_str`), thời gian còn lại (`_eta_str`).
  - Gửi log định kỳ vào log_callback.
- [ ] Giai đoạn FFmpeg extract audio:
  - Cập nhật tiến độ 92% -> 98% và ghi log `[FFmpeg] Đang trích xuất âm thanh 16kHz WAV...`.
  - Báo hoàn tất 100% khi audio file được tạo thành công.

### Phase 2: Quản lý Log & State trong FastAPI Backend (`app/main.py`)
- [ ] Khởi tạo danh sách `logs: []` trong `projects_db[project_id]`.
- [ ] Viết helper `append_project_log(project_id, message, level="INFO")` kèm timestamp `[HH:MM:SS]`. Giới hạn tối đa 200 dòng gần nhất để tránh phình bộ nhớ.
- [ ] Truyền `log_callback` từ `process_project_download_worker` vào `download_bilibili_video`.
- [ ] Đảm bảo endpoint `/api/project/{project_id}/status` trả về trường `logs`.

### Phase 3: Giao diện Terminal Console trên Frontend (`app/static/index.html`, `style.css`)
- [ ] Trong `app/static/index.html`:
  - Thêm thẻ HTML `#step1-terminal-box` ngay bên dưới `#step1-progress-box`.
  - Bao gồm:
    - Header: Badge `>_ Terminal Tiến Trình`, nút `Thu gọn / Mở rộng`, nút `Sao chép log`, nút `Xóa`.
    - Body: `#step1-terminal-logs` (pre/code-like container, auto-scroll).
- [ ] Trong `app/static/style.css`:
  - Style cho `.terminal-console-box`, `.terminal-header`, `.terminal-body`, `.terminal-log-line`.
  - Màu sắc cú pháp: thời gian xám nhạt, tag cyan/xanh lá/vàng/đỏ, font `Consolas, Menlo, Monaco, monospace`.
  - Hiệu ứng cuộn và transition mượt mà khi thu gọn.

### Phase 4: Frontend Logic & Polling Handler (`app/static/app.js`)
- [ ] Cập nhật hàm xử lý download trong `btnStep1Download.addEventListener`:
  - Reset và mở terminal khi bắt đầu tải.
  - Nhận mảng `statusData.logs` từ `/api/project/{id}/status`, render các dòng mới vào terminal.
  - Tự động cuộn xuống dưới cùng nếu người dùng không cuộn lên.
  - Xử lý các nút bấm: Toggle Collapse/Expand, Copy logs, Clear logs.
  - Đảm bảo hiển thị % mượt mà, đồng bộ giữa progress bar và text nhãn.

### Phase 5: Verification & Evidence
- [ ] Viết test tự động kiểm tra downloader hook và log formatting.
- [ ] Chạy test, kiểm tra server và ghi lại file `docs/superpowers/evidence/2026-10-31-download-progress-terminal.md`.

