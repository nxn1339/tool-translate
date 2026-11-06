# Implementation Plan: Tinh gọn App - Gỡ bỏ RVC và dọn dẹp rác hệ thống

- **Date:** 2026-11-01
- **Target:** Giải phóng >1.15 GB bộ nhớ, loại bỏ module RVC không cần thiết, làm sạch code backend/frontend và dọn dẹp các script debug rác trong `tests/`.

---

## Các Bước Triển Khai

### Phase 1: Xóa bỏ dữ liệu và mã nguồn RVC
- [ ] Xóa thư mục `rvc_backend/` (~663 MB).
- [ ] Xóa thư mục `app/models/rvc/` (~491 MB).
- [ ] Xóa file `app/rvc_engine.py`.

### Phase 2: Dọn dẹp thư mục `tests/`
- [ ] Giữ lại các test nghiệp vụ quan trọng:
  - `test_full_workflow.py`
  - `test_merger_direct.py`
  - `test_download_terminal.py`
  - `test_logo_overlay.py`
  - `test_pcm_mix.py`
  - `test_tts_api.py`
- [ ] Xóa 46 file script scratch debug tạm thời.

### Phase 3: Tinh gọn Backend (`app/main.py`, `app/tts.py`, `app/merger.py`)
- [ ] `app/tts.py`:
  - Lược bỏ tham số `rvc_model`, `rvc_pitch` trong `_compute_raw_tts_hash`, `_process_single_segment`, `_generate_all_segments`, `generate_tts_for_segments`.
  - Xóa bỏ khối mã gọi `convert_audio_segment_rvc`.
- [ ] `app/merger.py`:
  - Lược bỏ `rvc_model`, `rvc_pitch` trong hàm `generate_preview_audio_track`.
- [ ] `app/main.py`:
  - Xóa endpoint `@app.get("/api/rvc-models")`.
  - Xóa endpoint thừa `@app.post("/api/tts-free")`.
  - Bỏ `rvc_model`, `rvc_pitch` trong metadata mặc định và các Pydantic models (`ProjectUpdateRequest`, `ProjectRenderRequest`, `ProjectGenerateTTSRequest`).
  - Cập nhật các worker và endpoint gọi TTS / Render.

### Phase 4: Tinh gọn Frontend (`index.html`, `app.js`)
- [ ] `app/static/index.html`:
  - Lược bỏ UI chọn RVC model và thanh chỉnh pitch trong Bước 3.
  - Xóa navigation cũ ẩn `tabs-nav d-none`.
- [ ] `app/static/app.js`:
  - Lược bỏ logic fetch `/api/rvc-models`.
  - Bỏ `rvc_model`, `rvc_pitch` trong payload gửi lên backend.

### Phase 5: Verification
- [ ] Chạy kiểm tra cú pháp Python (`python -m py_compile`).
- [ ] Chạy `test_tts_api.py` hoặc kiểm tra khởi động app để đảm bảo không còn import lỗi hay vướng dependency.

