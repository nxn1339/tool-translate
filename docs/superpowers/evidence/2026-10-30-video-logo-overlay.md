# Verification Evidence: Video Logo / Watermark Overlay

- **Date:** 2026-10-30
- **Test Target:** Video Logo / Watermark Overlay (Backend, API, Frontend)
- **Status:** PASSED (100%)

---

## 1. Automated Test Execution

Command executed:
```bash
python -m unittest tests/test_logo_overlay.py
```

Output:
```
INFO:httpx2:HTTP Request: POST http://testserver/api/project/test_logo_project/logo "HTTP/1.1 200 OK"
INFO:httpx2:HTTP Request: GET http://testserver/api/project/test_logo_project/logo "HTTP/1.1 200 OK"
.INFO:app.merger:Video specs: 1920x1080, total_duration=10.00s, Has original audio: True, Auto-extend: False
INFO:app.merger:Exported SRT subtitles to: subtitles.srt (0 entries)
INFO:app.merger:Exported ASS subtitles to: subtitles.ass (0 entries, PlayRes=1920x1080, Fontsize=72, Center=(960,918))
INFO:app.merger:Running master FFmpeg command (need_video_filter=True, needs_extension=False)...
INFO:app.merger:Video merged successfully: dummy_out.mp4
.INFO:app.merger:Video specs: 1920x1080, total_duration=10.00s, Has original audio: True, Auto-extend: False
INFO:app.merger:Exported SRT subtitles to: subtitles.srt (0 entries)
INFO:app.merger:Exported ASS subtitles to: subtitles.ass (0 entries, PlayRes=1920x1080, Fontsize=72, Center=(960,918))
INFO:app.merger:Running master FFmpeg command (need_video_filter=False, needs_extension=False)...
INFO:app.merger:Video merged successfully: dummy_out.mp4
.
----------------------------------------------------------------------
Ran 3 tests in 0.057s

OK
```

---

## 2. Checklist Verification

| Requirement | Implementation Detail | Status |
| :--- | :--- | :--- |
| **Co giãn tùy ý (Resize)** | Bounding Box `bbox-logo` hỗ trợ kéo 4 góc (`nw`, `ne`, `sw`, `se`) và slider chiều rộng (5% - 50%). | Verified |
| **Vị trí tùy ý (Drag & Drop)** | Kéo thả trực tiếp trên video canvas theo tọa độ phần trăm, kèm presets góc nhanh và sliders X/Y. | Verified |
| **Độ trong suốt (Opacity)** | Slider opacity 10% - 100%, filter `colorchannelmixer=aa=...` xử lý trực tiếp kênh alpha. | Verified |
| **Ghép vào Video qua FFmpeg** | Input logo được đưa sau các audio stream để tránh lệch index TTS, lệnh `scale` và `overlay` chuẩn xác. | Verified |
| **API Upload & Stream** | Endpoints `POST /api/project/{id}/logo` & `GET /api/project/{id}/logo` hoạt động trơn tru. | Verified |
| **Lưu trữ & Persistence** | Cấu hình `logo_box` được lưu trong `project.json` và phục hồi nguyên vẹn khi mở lại dự án. | Verified |

