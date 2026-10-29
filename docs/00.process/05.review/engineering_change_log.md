# Engineering Change Log - Nhật ký thay đổi kỹ thuật

| Mã thay đổi | Slice | Phân loại | Mô tả tóm tắt | File ảnh hưởng | Tác giả | Ngày |
|---|---|---|---|---|---|---|
| `CHG-001` | `VS-005` | `feature` | Triển khai giao diện 3 Tab, Canvas kéo thả 2 Bounding Box và Tab 3 Cài đặt | `app/static/index.html`, `app/static/style.css`, `app/static/app.js` | Dev | 2026-10-24 |
| `CHG-002` | `VS-005` | `feature` | Tích hợp RapidOCR quét chữ tiếng Trung từ frame trong vùng chọn và gom cụm timeline | `app/ocr.py`, `requirements.txt` | Dev | 2026-10-24 |
| `CHG-003` | `VS-005` | `feature` | Nâng cấp FFmpeg filter áp dụng Masking (Blur/Solid) che sub cũ và in Hardsub tiếng Việt | `app/merger.py` | Dev | 2026-10-24 |
| `CHG-004` | `VS-005` | `feature` | Bổ sung API endpoints `/api/translate-ocr`, `/api/subtitles/{task_id}`, `/api/tts-free` | `app/main.py` | Dev | 2026-10-24 |
| `CHG-005` | `Foundation`| `refactor` | Kích hoạt `reload=True` trong `run.py` để server tự động cập nhật khi mã nguồn thay đổi | `run.py` | Dev | 2026-10-24 |
