# Test Coverage Matrix

| Test Case ID | Tiêu đề kiểm thử | Slice | Req ID liên kết | Mức độ ưu tiên | Loại kiểm thử | Trạng thái hiện tại |
|---|---|---|---|---|---|---|
| `TC-001` | Kiểm tra tải video và audio từ Bilibili URL hợp lệ | `VS-001` | `REQ-001` | High | Integration | Passed |
| `TC-002` | Kiểm tra sinh buvid3/buvid4 khi không có cookie | `VS-003` | `REQ-002` | High | Unit | Passed |
| `TC-003` | Kiểm tra Whisper nhận diện giọng nói và xuất timestamp | `VS-001` | `REQ-003` | High | Unit | Passed |
| `TC-004` | Kiểm tra Google Translate dịch câu thoại tiếng Trung | `VS-001` | `REQ-004` | High | Integration | Passed |
| `TC-005` | Kiểm tra CapCut / Edge-TTS sinh file mp3 đúng giọng cấu hình | `VS-004` | `REQ-005` | High | Integration | Passed |
| `TC-006` | Kiểm tra FFmpeg ghép audio TTS vào video gốc | `VS-001` | `REQ-006` | High | Integration | Passed |
| `TC-007` | Kiểm tra submit form trên UI gửi đúng payload | `VS-002` | `REQ-007` | Medium | E2E | Passed |
| `TC-008` | Kiểm tra thanh tiến độ cập nhật đúng theo task state | `VS-002` | `REQ-008` | Medium | E2E | Passed |
| `TC-009` | Kiểm tra link tải file mp4 trả về đúng video | `VS-002` | `REQ-009` | High | E2E | Passed |
| `TC-010` | Kiểm tra nhận diện binary `ffmpeg/ffmpeg.exe` local | `VS-001` | `REQ-010` | Critical | Unit / System | Passed |
| `TC-011` | Kiểm tra chuyển đổi 4 Bước Studio không mất dữ liệu | `VS-005` | `REQ-013` | High | UI / E2E | Passed |
| `TC-012` | Kéo thả & co giãn Khung Che Sub cũ (Mask Box) | `VS-005` | `REQ-014` | High | UI / Canvas | Passed |
| `TC-013` | Định vị độc lập Khung Sub Việt (Subtitle Box) | `VS-005` | `REQ-015` | High | UI / Canvas | Passed |
| `TC-014` | Rapid/PaddleOCR quét chữ tiếng Trung & gom timeline | `VS-005` | `REQ-016` | Critical | Integration | Passed |
| `TC-015` | FFmpeg che sub cũ & in Hardsub tiếng Việt ASS | `VS-005` | `REQ-017` | Critical | Integration | Passed |
| `TC-016` | Xuất và tải file phụ đề rời `.srt` hợp lệ | `VS-005` | `REQ-018` | Medium | Integration / API | Passed |
| `TC-017` | Quản lý dự án đa phiên & đồng bộ cấu hình | `VS-005` | `REQ-019` | High | E2E | Passed |
| `TC-018` | Video không có chữ khi quét ở Bước 2 (Negative) | `VS-005` | `REQ-016` | Medium | Edge Case | Passed |
| `TC-019` | Khống chế biên khi kéo khung ra ngoài (Boundary) | `VS-005` | `REQ-014` | Low | UI / Canvas | Passed |
| `TC-020` | Gom cụm frame trùng lặp & khử nhấp nháy sub | `VS-005` | `REQ-016` | Medium | Unit / Alg | Passed |
| `TC-021` | Tương thích video dọc 9:16 vs video ngang 16:9 | `VS-005` | `REQ-017` | High | Integration | Passed |
| `TC-022` | Upload file ảnh Logo dự án qua API và Studio UI | `VS-006` | `REQ-020`, `REQ-021` | High | Integration / API | Passed |
| `TC-023` | Kéo thả di chuyển & co giãn 8 chốt kích thước Logo | `VS-006` | `REQ-024` | Critical | UI / Canvas | Passed |
| `TC-024` | Tùy chỉnh độ mờ Opacity và khóa tỷ lệ aspect ratio | `VS-006` | `REQ-023` | High | UI / Canvas | Passed |
| `TC-025` | Phím tắt xóa nhanh Logo (Delete) và các Preset vị trí | `VS-006` | `REQ-025` | High | UI / Canvas | Passed |
| `TC-026` | FFmpeg render video thành phẩm tích hợp Logo Watermark | `VS-006` | `REQ-022`, `REQ-023` | Critical | Integration / FFmpeg | Passed |
