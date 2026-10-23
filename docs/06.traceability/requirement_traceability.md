# Requirement Traceability Matrix (RTM)

Ma trận truy vết từ Yêu cầu nghiệp vụ -> User Story -> Màn hình UI -> API -> Mã nguồn / Worker -> Test Case.

| Req ID | Tiêu đề yêu cầu | Slice | User Story | Màn hình | API ID | Thành phần xử lý | Test Case ID | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| `REQ-001` | Tải video & tách audio từ Bilibili URL | `VS-001` | `US-001` | `APP-001` | `API-001` | `app/downloader.py` | `TC-001` | Implemented |
| `REQ-002` | Tự động tạo cookie buvid3/buvid4 chống 412 | `VS-003` | `US-002` | `APP-001` | `API-001` | `app/downloader.py` | `TC-002` | Implemented |
| `REQ-003` | Nhận dạng giọng nói (STT) qua Whisper local | `VS-001` | `US-003` | `APP-001` | `API-001` | `app/translator.py` | `TC-003` | Implemented |
| `REQ-004` | Dịch đoạn phụ đề tiếng Trung sang tiếng Việt | `VS-001` | `US-004` | `APP-001` | `API-001` | `app/translator.py` | `TC-004` | Implemented |
| `REQ-005` | Khởi tạo giọng lồng tiếng Việt qua Edge-TTS | `VS-004` | `US-005` | `APP-001` | `API-001` | `app/tts.py` | `TC-005` | Implemented |
| `REQ-006` | Trộn âm thanh TTS và nhạc nền vào video gốc | `VS-001` | `US-006` | `APP-001` | `API-001` | `app/merger.py` | `TC-006` | Implemented |
| `REQ-007` | Giao diện Web Dashboard nhập URL & tùy chỉnh | `VS-002` | `US-007` | `APP-001` | `API-001`, `API-002` | `app/static/index.html` | `TC-007` | Implemented |
| `REQ-008` | Polling cập nhật tiến độ tác vụ real-time | `VS-002` | `US-008` | `APP-001` | `API-002` | `app/main.py:get_task_status` | `TC-008` | Implemented |
| `REQ-009` | Tải về video thành phẩm hoàn thiện | `VS-002` | `US-009` | `APP-001` | `API-003` | `app/main.py:download_video` | `TC-009` | Implemented |
| `REQ-010` | Khắc phục sai lệch đường dẫn FFmpeg local | `VS-001` | `US-010` | N/A | N/A | `run.py`, `app/downloader.py` | `TC-010` | Open (Refactor) |
