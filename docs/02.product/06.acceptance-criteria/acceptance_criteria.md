# Acceptance Criteria Template & Index

| AC ID | Tiêu đề | Điều kiện nghiệm thu (Given - When - Then) | Req ID |
|---|---|---|---|
| `AC-001` | Tải video thành công | Given: Link Bilibili hợp lệ.<br>When: Nhấn "Bắt đầu".<br>Then: Server tải thành công file mp4 và tách wav vào thư mục temp. | `REQ-001` |
| `AC-002` | Whisper STT chuẩn xác | Given: File wav có tiếng người nói.<br>When: Model Whisper transcribe hoàn tất.<br>Then: Danh sách segments có timestamp start/end hợp lệ và text không rỗng. | `REQ-003` |
| `AC-003` | Xuất video lồng tiếng | Given: Các đoạn voice TTS đã sinh.<br>When: FFmpeg hoàn thành lệnh mix.<br>Then: File `output_dubbed.mp4` phát được, có cả hình ảnh và âm thanh thoại tiếng Việt. | `REQ-006` |
